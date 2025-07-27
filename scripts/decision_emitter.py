from mab_algo import (
    SimpleAverage,
    EpsilonGreedy
)
from typing import List
from app.database import (
    MongoDB,
    Results,
    Event,
)
from app.messaging import (
    RabbitMQ,
    RELAY_QUEUE,
    DecisionMessage,
    LogMessage,
    LOGS_EXCHANGE,
)
from app.config import (
    PROCESS_FRAMES,
    Decision
)

mongo_client = MongoDB()
rabbit_mq = RabbitMQ()


def publish_to_relay(action: str) -> None:
    """
    Helper method to publish to Relay Queue to emit
    decisions.

    Args:
        action (str): The action to emit, based on RL algo.
    """
    rabbit_mq.publish_to_queue(
        queue=RELAY_QUEUE,
        message=DecisionMessage(decision=int(action))
    )


# Set up the Reinforcement learning algorithm.
algo = EpsilonGreedy(
    actions=['0', '1'],
    averager=SimpleAverage(),
    epsilon=0.5
)

action = algo.step()
# Publish initial data to start the sequence.
publish_to_relay(action)
current_action = action

# Watch the 'Results' collection for updates.
# Once a set amount (as denoted by the env 'PROCESS_FRAMES')
# is reached. THe average reward is calculated and passed to
# the reinforcement learning algorithm, which decides the next
# action. This next action is then published to the relay and log queue.
for change in mongo_client.watch_collection(Results, Event.INSERT):
    if mongo_client.get_collection_size(Results) > PROCESS_FRAMES:
        documents: List[Results] = mongo_client.get_documents(
            Results,
            oldest=True,
            quantity=PROCESS_FRAMES,
            delete=True
        )
        # Average the reward to aid in making a decision.
        avg_reward = sum(
            document.result
            for document in documents
        ) / PROCESS_FRAMES
        action = algo.step(reward=avg_reward)
        publish_to_relay(action)
        change_msg = (
            f'{Decision(int(current_action)).name} ',
            f' -> {Decision(int(action)).name}'
        )
        rabbit_mq.publish(
            LOGS_EXCHANGE,
            LogMessage(
                terminal_message=change_msg,
                file_message=change_msg
            )
        )
        if current_action != action:
            current_action = action
            # If the stream is swapped, then the databases have to
            # be flushed to process the next set of data.
            mongo_client.flush_database()
