from tests_private_api.tests_http_requests.test_client import run_local_api_tests, run_remote_api_tests
from tests_private_api.tests_mongo_queries.test_mongo import run_mongo_tests


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("type", type=str, help="api or mongo")
    parser.add_argument("--loc", type=str, help="local or remote")
    args = parser.parse_args()

    if args.type == "mongo":
        run_mongo_tests()
    elif args.type == "http": 
        if args.loc == "local":
            run_local_api_tests()
        else:
            run_remote_api_tests()
