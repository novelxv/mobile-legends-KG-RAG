from database import GraphDatabaseDriver
from response_generator import ResponseGenerator
from text_to_cypher import TextToCypher

with GraphDatabaseDriver() as driver:
    with open("schema_example.txt") as fp:
        schema = fp.read().strip()

    print("Preparing text-to-Cypher pipeline ....")
    ttc = TextToCypher(schema)

    print("Preparing response generator pipeline ....")
    generator = ResponseGenerator(schema)

    interrupt = False
    print("(Interrupt to stop.)")
    print("TIP: Try questions like 'List all marksman heroes' or 'Who is Layla?'\n")
    
    while not interrupt:
        try:
            question = input("Question: ")
        except KeyboardInterrupt:
            interrupt = True

        if not interrupt and question.strip():
            print("Generating Cypher query ....")
            query = ttc(question)
            print(query)

            print("Executing Cypher query ....")
            try:
                results = driver.execute_query(query)
            except Exception as e:
                print(f"❌ Query execution failed: {e}")
                results = []
            
            if len(results) > 0:
                # Limit display for readability
                display_limit = 20
                if len(results) > display_limit:
                    query_result_str = "\n".join([
                        str(x) for x in results[:display_limit]
                    ])
                    query_result_str += f"\n... and {len(results) - display_limit} more results"
                else:
                    query_result_str = "\n".join([
                        str(x) for x in results
                    ])
            else:
                query_result_str = "(no results found)"
            print(query_result_str)

            if results:
                print("Generating response ....")
                response = generator(question, query, query_result_str)
                print(f"\n💬 {response}\n")
            else:
                print("\n❌ No results found.\n")
    
    print("(Stopped.)")
