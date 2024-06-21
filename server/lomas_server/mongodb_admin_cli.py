import argparse

from pymongo import MongoClient
from pymongo.database import Database

from admin_database.utils import get_mongodb_url
from mongodb_admin import (
    add_dataset,
    add_dataset_to_user,
    add_datasets_via_yaml,
    add_user,
    add_user_with_budget,
    add_users_via_yaml,
    del_dataset,
    del_dataset_to_user,
    del_user,
    drop_collection,
    get_list_of_datasets,
    get_list_of_datasets_from_user,
    get_list_of_users,
    set_budget_field,
    set_may_query,
    show_archives_of_user,
    show_collection,
    show_dataset,
    show_metadata_of_dataset,
    show_user,
)

if __name__ == "__main__":
    ########################################################################
    ########################## MongoDB Connection ############# # noqa: E266
    ########################################################################
    connection_parser = argparse.ArgumentParser(add_help=False)
    connection_parser.add_argument("-db_u", "--username", default="user")
    connection_parser.add_argument("-db_pwd", "--password", default="user_pwd")
    connection_parser.add_argument("-db_a", "--address", default="mongodb")
    connection_parser.add_argument("-db_p", "--port", default=27017)
    connection_parser.add_argument("-db_n", "--db_name", default="defaultdb")

    ########################################################################
    ######################## MongoDB Administration ############ # noqa: E266
    ########################################################################
    parser = argparse.ArgumentParser(
        description="MongoDB administration script for the database"
    )
    subparsers = parser.add_subparsers(
        title="subcommands", help="user database administration operations"
    )

    ##########################  USERS  ########################## # noqa: E266
    # Create the parser for the "add_user" command
    add_user_parser = subparsers.add_parser(
        "add_user",
        help="add user to users collection",
        parents=[connection_parser],
    )
    add_user_parser.add_argument("-u", "--user", required=True, type=str)
    add_user_parser.set_defaults(func=add_user)

    # Create the parser for the "add_user_with_budget" command
    add_user_wb_parser = subparsers.add_parser(
        "add_user_with_budget",
        help="add user with budget to users collection",
        parents=[connection_parser],
    )
    add_user_wb_parser.add_argument("-u", "--user", required=True, type=str)
    add_user_wb_parser.add_argument("-d", "--dataset", required=True, type=str)
    add_user_wb_parser.add_argument(
        "-e", "--epsilon", required=True, type=float
    )
    add_user_wb_parser.add_argument(
        "-del", "--delta", required=True, type=float
    )
    add_user_wb_parser.set_defaults(func=add_user_with_budget)

    # Create the parser for the "del_user" command
    del_user_parser = subparsers.add_parser(
        "del_user",
        help="delete user from users collection",
        parents=[connection_parser],
    )
    del_user_parser.add_argument("-u", "--user", required=True, type=str)
    del_user_parser.set_defaults(func=del_user)

    # Create the parser for the "add_dataset" command
    add_dataset_to_user_parser = subparsers.add_parser(
        "add_dataset_to_user",
        help="add dataset with initialized budget values for a user",
        parents=[connection_parser],
    )
    add_dataset_to_user_parser.add_argument(
        "-u", "--user", required=True, type=str
    )
    add_dataset_to_user_parser.add_argument(
        "-d", "--dataset", required=True, type=str
    )
    add_dataset_to_user_parser.add_argument(
        "-e", "--epsilon", required=True, type=float
    )
    add_dataset_to_user_parser.add_argument(
        "-del", "--delta", required=True, type=float
    )
    add_dataset_to_user_parser.set_defaults(func=add_dataset_to_user)

    # Create the parser for the "del_dataset" command
    del_dataset_to_user_parser = subparsers.add_parser(
        "del_dataset_to_user",
        help="delete dataset for user in users collection",
        parents=[connection_parser],
    )
    del_dataset_to_user_parser.add_argument(
        "-u", "--user", required=True, type=str
    )
    del_dataset_to_user_parser.add_argument(
        "-d", "--dataset", required=True, type=str
    )
    del_dataset_to_user_parser.set_defaults(func=del_dataset_to_user)

    # Create the parser for the "set_budget_field" command
    set_budget_field_parser = subparsers.add_parser(
        "set_budget_field",
        help="set budget field to given value for given user and dataset",
        parents=[connection_parser],
    )
    set_budget_field_parser.add_argument(
        "-u", "--user", required=True, type=str
    )
    set_budget_field_parser.add_argument(
        "-d", "--dataset", required=True, type=str
    )
    set_budget_field_parser.add_argument(
        "-f",
        "--field",
        required=True,
        choices=["initial_epsilon", "initial_delta"],
    )
    set_budget_field_parser.add_argument(
        "-v", "--value", required=True, type=float
    )
    set_budget_field_parser.set_defaults(func=set_budget_field)

    # Create the parser for the "set_may_query" command
    set_may_query_parser = subparsers.add_parser(
        "set_may_query",
        help="set may query field to given value for given user",
        parents=[connection_parser],
    )
    set_may_query_parser.add_argument("-u", "--user", required=True, type=str)
    set_may_query_parser.add_argument(
        "-v", "--value", required=True, choices=["False", "True"]
    )
    set_may_query_parser.set_defaults(func=set_may_query)

    # Show the user
    show_user_parser = subparsers.add_parser(
        "show_user",
        help="show all metadata of user",
        parents=[connection_parser],
    )
    show_user_parser.add_argument("-u", "--user", required=True, type=str)
    show_user_parser.set_defaults(func=show_user)

    # Create the parser for the "create_example_users" command
    users_collection_from_yaml_parser = subparsers.add_parser(
        "add_users_via_yaml",
        help="create users collection from yaml file",
        parents=[connection_parser],
    )
    users_collection_from_yaml_parser.add_argument(
        "-c",
        "--clean",
        required=False,
        action="store_const",
        const=True,
        default=False,
    )
    users_collection_from_yaml_parser.add_argument(
        "-o",
        "--overwrite",
        required=False,
        action="store_const",
        const=True,
        default=False,
    )
    users_collection_from_yaml_parser.add_argument(
        "-yf", "--yaml_file", required=True, type=str
    )
    users_collection_from_yaml_parser.set_defaults(func=add_users_via_yaml)

    # Function: Show Archives of User
    show_archives_parser = subparsers.add_parser(
        "show_archives_of_user",
        help="show all previous queries from a user",
        parents=[connection_parser],
    )
    show_archives_parser.add_argument(
        "-u",
        "--user",
        required=True,
        type=str,
        help="username of the user to show archives",
    )
    show_archives_parser.set_defaults(func=show_archives_of_user)

    # Function: Get List of Users
    get_users_parser = subparsers.add_parser(
        "get_list_of_users",
        help="get the list of all users in 'users' collection",
        parents=[connection_parser],
    )
    get_users_parser.set_defaults(func=get_list_of_users)

    # Function: Get List of Datasets from User
    get_user_datasets_parser = subparsers.add_parser(
        "get_list_of_datasets_from_user",
        help="get the list of all datasets from a user",
        parents=[connection_parser],
    )
    get_user_datasets_parser.add_argument(
        "-u",
        "--user",
        required=True,
        type=str,
        help="username of the user to show datasets",
    )
    get_user_datasets_parser.set_defaults(func=get_list_of_datasets_from_user)

    #######################  DATASETS  ####################### # noqa: E266
    # Create parser for dataset private database
    add_dataset_parser = subparsers.add_parser(
        "add_dataset",
        help="set in which database the dataset is stored",
        parents=[connection_parser],
    )
    # Dataset location
    add_dataset_parser.add_argument("-d", "--dataset_name", required=True)
    add_dataset_parser.add_argument("-db", "--database_type", required=True)
    add_dataset_parser.add_argument(
        "-d_path", "--dataset_path", required=False
    )
    add_dataset_parser.add_argument("-s3b", "--s3_bucket", required=False)
    add_dataset_parser.add_argument("-s3k", "--s3_key", required=False)
    add_dataset_parser.add_argument(
        "-s3_url", "--endpoint_url", required=False
    )
    add_dataset_parser.add_argument(
        "-s3_ak", "--aws_access_key_id", required=False
    )
    add_dataset_parser.add_argument(
        "-s3_sak", "--aws_secret_access_key", required=False
    )
    # Metadata location
    add_dataset_parser.add_argument(
        "-m_db", "--metadata_database_type", required=True
    )
    add_dataset_parser.add_argument("-mp", "--metadata_path", required=False)
    add_dataset_parser.add_argument(
        "-m_s3b", "--metadata_s3_bucket", required=False
    )
    add_dataset_parser.add_argument(
        "-m_s3k", "--metadata_s3_key", required=False
    )
    add_dataset_parser.add_argument(
        "-m_s3_url", "--metadata_endpoint_url", required=False
    )
    add_dataset_parser.add_argument(
        "-m_s3_ak", "--metadata_aws_access_key_id", required=False
    )
    add_dataset_parser.add_argument(
        "-m_s3_sak", "--metadata_aws_secret_access_key", required=False
    )
    add_dataset_parser.set_defaults(func=add_dataset)

    # Create the parser for the "add_datasets_via_yaml" command
    add_datasets_via_yaml_parser = subparsers.add_parser(
        "add_datasets_via_yaml",
        help="create dataset to database type collection",
        parents=[connection_parser],
    )
    add_datasets_via_yaml_parser.add_argument(
        "-yf", "--yaml_file", required=True, type=str
    )
    add_datasets_via_yaml_parser.add_argument(
        "-c",
        "--clean",
        required=False,
        action="store_const",
        const=True,
        default=False,
    )
    add_datasets_via_yaml_parser.add_argument(
        "-od",
        "--overwrite_datasets",
        required=False,
        action="store_const",
        const=True,
        default=False,
    )
    add_datasets_via_yaml_parser.add_argument(
        "-om",
        "--overwrite_metadata",
        required=False,
        action="store_const",
        const=True,
        default=False,
    )
    add_datasets_via_yaml_parser.set_defaults(func=add_datasets_via_yaml)

    # Create the parser for the "del_dataset" command
    del_dataset_parser = subparsers.add_parser(
        "del_dataset",
        help="delete dataset and metadata from "
        "datasets and metadata collection",
        parents=[connection_parser],
    )
    del_dataset_parser.add_argument("-d", "--dataset", required=True, type=str)
    del_dataset_parser.set_defaults(func=del_dataset)

    # Function: Show Dataset
    show_dataset_parser = subparsers.add_parser(
        "show_dataset",
        help="show a dataset from the dataset collection",
        parents=[connection_parser],
    )
    show_dataset_parser.add_argument(
        "-d",
        "--dataset",
        required=True,
        type=str,
        help="name of the dataset to show",
    )
    show_dataset_parser.set_defaults(func=show_dataset)

    # Function: Show Metadata of Dataset
    show_metadata_parser = subparsers.add_parser(
        "show_metadata_of_dataset",
        help="show metadata from the metadata collection",
        parents=[connection_parser],
    )
    show_metadata_parser.add_argument(
        "-d",
        "--dataset",
        required=True,
        type=str,
        help="name of the dataset of the metadata to show",
    )
    show_metadata_parser.set_defaults(func=show_metadata_of_dataset)

    # Function: Get List of Datasets
    get_datasets_parser = subparsers.add_parser(
        "get_list_of_datasets",
        help="get the list of all datasets in 'datasets' collection",
        parents=[connection_parser],
    )
    get_datasets_parser.set_defaults(func=get_list_of_datasets)

    #######################  COLLECTIONS  ####################### # noqa: E266
    # Create the parser for the "drop_collection" command
    drop_collection_parser = subparsers.add_parser(
        "drop_collection",
        help="delete collection from database",
        parents=[connection_parser],
    )
    drop_collection_parser.add_argument(
        "-c",
        "--collection",
        required=True,
        choices=["users", "datasets", "metadata", "queries_archives"],
    )
    drop_collection_parser.set_defaults(func=drop_collection)

    # Create the parser for the "show_users_collection" command
    show_collection_parser = subparsers.add_parser(
        "show_collection",
        help="print a collection",
        parents=[connection_parser],
    )
    show_collection_parser.add_argument(
        "-c",
        "--collection",
        required=True,
        choices=["users", "datasets", "metadata", "queries_archives"],
    )
    show_collection_parser.set_defaults(func=show_collection)

    args = parser.parse_args()

    #######################  FUNCTION CALL  ###################### # noqa: E266
    # Get MongoDB
    db_url = get_mongodb_url(args)
    mongo_db: Database = MongoClient(db_url)[args.db_name]

    function_map = {
        "add_user": lambda args: add_user(mongo_db, args.user),
        "add_user_with_budget": lambda args: add_user_with_budget(
            mongo_db, args.user, args.dataset, args.epsilon, args.delta
        ),
        "del_user": lambda args: del_user(mongo_db, args.user),
        "add_dataset_to_user": lambda args: add_dataset_to_user(
            mongo_db, args.user, args.dataset, args.epsilon, args.delta
        ),
        "del_dataset_to_user": lambda args: del_dataset_to_user(
            mongo_db, args.user, args.dataset
        ),
        "set_budget_field": lambda args: set_budget_field(
            mongo_db, args.user, args.dataset, args.field, args.value
        ),
        "set_may_query": lambda args: set_may_query(
            mongo_db, args.user, args.value
        ),
        "show_user": lambda args: show_user(mongo_db, args.user),
        "add_users_via_yaml": lambda args: add_users_via_yaml(
            mongo_db, args.yaml_file, args.clean, args.overwrite
        ),
        "show_archives_of_user": lambda args: show_archives_of_user(
            mongo_db, args.user
        ),
        "get_list_of_users": lambda args: get_list_of_users(mongo_db),
        "get_list_of_datasets_from_user": lambda args: get_list_of_datasets_from_user(
            mongo_db, args.user
        ),
        "add_dataset": lambda args: add_dataset(
            mongo_db,
            args.dataset_name,
            args.database_type,
            args.metadata_database_type,
            args.dataset_path,
            args.metadata_path,
            args.s3_bucket,
            args.s3_key,
            args.endpoint_url,
            args.aws_access_key_id,
            args.aws_secret_access_key,
            args.metadata_s3_bucket,
            args.metadata_s3_key,
            args.metadata_endpoint_url,
            args.metadata_aws_access_key_id,
            args.metadata_aws_secret_access_key,
        ),
        "add_datasets_via_yaml": lambda args: add_datasets_via_yaml(
            mongo_db,
            args.yaml_file,
            args.clean,
            args.overwrite_datasets,
            args.overwrite_metadata,
        ),
        "del_dataset": lambda args: del_dataset(mongo_db, args.dataset),
        "show_dataset": lambda args: show_dataset(mongo_db, args.dataset),
        "show_metadata_of_dataset": lambda args: show_metadata_of_dataset(
            mongo_db, args.dataset
        ),
        "get_list_of_datasets": lambda args: get_list_of_datasets(mongo_db),
        "drop_collection": lambda args: drop_collection(
            mongo_db, args.collection
        ),
        "show_collection": lambda args: show_collection(
            mongo_db, args.collection
        ),
    }
    function_map[args.func.__name__](args)
