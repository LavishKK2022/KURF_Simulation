from app.database import (
    MongoModel,
    Event,
    URL,
    DATABASE,
    generate_bson_schema,
)
from pymongo import (
    ASCENDING,
    MongoClient as connect,
)
from pymongo.collection import (
    Collection,
)
from typing import (
    Generator,
    Optional,
    List,
    Any,
    Type,
    Union,
    Dict,
)
from bson.objectid import ObjectId


class MongoDB:
    """ MongoDB helper singleton class """
    _instance = None

    def __new__(cls):
        """ Method to ensure MongoDB class is singleton """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Connects to the database
            cls._instance._connect()
            # Initialise the database
            cls._instance._create_database()
            # Creates the collections 
            cls._instance._create_collections()
        return cls._instance

    def _connect(self) -> None:
        """ Connect to the MongoDB database """
        self._client = connect(URL)[DATABASE]

    def _create_database(self) -> None:
        """ Creates the MongoDB database """
        self._db = self._client[DATABASE]

    def _create_collections(self) -> None:
        """ Creates the MongoDB collections (with schemas) """
        for collection in MongoModel.__subclasses__():
            # Dynamic generation of MongoDB schema.
            self._db.create_collection(
                collection.__name__,
                validator=generate_bson_schema(collection)
            )

    def get_collection(
            self,
            collection: Type[MongoModel]
    ) -> Collection:
        """
        Retrieves the MongoDB collection from MongoModel mapping.

        Args:
            collection (Type[MongoModel]): The MongoModel mapping.

        Returns:
            Collection: The MongoDB collection.
        """
        return self._db[collection.__name__]

    def get_collection_size(
            self,
            collection: Type[MongoModel]
    ) -> int:
        """
        Retrieves the size of the collection from MongoModel mapping.

        Args:
            collection (Type[MongoModel]): The MongoModel mapping.

        Returns:
            int: The size of the collection.
        """
        return self.get_collection(collection).count_documents({})

    def _delete_documents(
            self,
            collection: Type[MongoModel],
            documents: List[MongoModel]
    ) -> None:
        """
        Delete documents from the MongoDB database.

        Args:
            collection (Type[MongoModel]): The collection from which
            to delete from.

            documents (List[MongoModel]): The documents to delete.
        """
        delete_ids = [document.id for document in documents]
        self.get_collection(collection).delete_many(
            {'_id': {'$in': delete_ids}}
        )

    def get_document_by_id(
            self,
            collection: Type[MongoModel],
            id: Union[str, ObjectId],
    ) -> Optional[MongoModel]:
        """
        Retrieve documents by ID, if they exist in the database.
        THe return document is wrapped in the collection BaseModel.

        Args:
            collection (Type[MongoModel]): The collection to search from.
            id (Union[str, ObjectId]): The document ID to search for.

        Returns:
            Optional[MongoModel]: The document wrapped in the BaseModel.
        """
        result = self.get_collection(collection).find_one(
            {'_id': ObjectId(id)}
        )
        return collection(**result) if result else None

    def get_documents(
            self,
            collection: Type[MongoModel],
            oldest: bool = True,
            quantity: int = 0,
            delete: bool = False
    ) -> List[MongoModel]:
        """
        Get documents from the MongoDB 'collection.'
        Applies a number of operations on the data.

        Args:
            collection (Type[MongoModel]): The collection to retrieve from.
            oldest (bool, optional): Retrieve data in ASCENDING format.
            quantity (int, optional): Limit query results.
            delete (bool, optional): Delete data upon retrieval.

        Returns:
            List[MongoModel]: List of wrapped documents with the
            operations applied.
        """
        cursor = self.get_collection(collection).find({})
        if oldest:
            cursor = cursor.sort('_id', ASCENDING)
        if quantity:
            cursor = cursor.limit(quantity)

        documents = [collection(**document) for document in cursor]

        if delete and documents:
            self._delete_documents(collection, documents)
        return documents

    def upsert_document(
            self,
            collection: Type[MongoModel],
            filter: Dict[str, Any],
            update: Dict[str, Any]
    ) -> None:
        """
        Upsert documents into the MongoDB database.

        Args:
            collection (Type[MongoModel]): The collection
            to upsert into.

            filter (Dict[str, Any]): Operation to filter
            the documents.

            update (Dict[str, Any]): The update operations
            to apply.
        """
        self.get_collection(collection).update_one(
            filter,
            update,
            upsert=True
        )

    def insert_document(
            self,
            collection: Type[MongoModel],
            record: MongoModel
    ) -> None:
        """
        Insert documents into the MongoDB database.
        The document must be wrapped in the appropriate
        MongoModel.

        Args:
            collection (Type[MongoModel]): The collection
            to update to.

            record (MongoModel): The document to upload.
        """
        self.get_collection(collection).insert_one(
            **record.model_dump(
                by_alias=True,
                exclude_none=True
            )
        )

    def flush_database(self) -> None:
        """ Delete the documents """
        for collection in MongoModel.__subclasses__():
            self.get_collection(collection).remove({})

    def watch_collection(
            self,
            collection: Type[MongoModel],
            event: Event
    ) -> Generator[ObjectId, Any, Any]:
        """
        Applies a watch on a MongoDB collection for
        specific operations (denoted by Event).

        Args:
            collection (Type[MongoModel]): The collection
            to 'watch'

            event (Event): The operation to filter by.

        Yields:
            Generator[ObjectId, Any, Any]: The _id of the document that
            has resulted in a 'watch' event.
        """
        change_stream = self.get_collection(collection).watch([{
            '$match': {
                'operationType': {'$in': [f'{event}']}
            }
        }])
        for change in change_stream:
            yield ObjectId(change['documentKey'])
