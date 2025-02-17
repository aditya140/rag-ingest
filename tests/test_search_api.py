import requests
import json
from typing import Dict, Any

def test_search(query_config: Dict[str, Any]) -> None:
    """
    Test the search API with the given query configuration.
    
    Args:
        query_config (Dict[str, Any]): Search configuration including query and parameters
    """
    # API endpoint
    search_url = "http://localhost:8000/search"
    
    print(f"Executing search with config: {json.dumps(query_config, indent=2)}")
    
    try:
        # Make the search request
        response = requests.post(
            search_url,
            json=query_config,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            results = response.json()
            print("\nSearch Results:")
            print("-" * 80)
            
            for i, result in enumerate(results["results"], 1):
                print(f"\nResult {i}:")
                print(f"Score: {result['score']:.3f}")
                print(f"Document ID: {result['doc_id']}")
                print(f"Chunk ID: {result['chunk_id']}")
                print("\nText:")
                print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
                if result.get('metadata'):
                    print("\nMetadata:")
                    print(json.dumps(result['metadata'], indent=2))
                print("-" * 80)
                
        else:
            print(f"Search failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error during search: {str(e)}")

if __name__ == "__main__":
    # Example search configurations
    search_configs = [
        {
            "query": "What are the key features of the Deepseek model?",
            "required_keywords": ["deepseek", "model"],
            "similarity_threshold": 0.7,
            "hybrid_alpha": 0.3,
            "limit": 5
        },
        {
            "query": "Explain the model architecture and training process",
            "similarity_threshold": 0.3,
            "required_keywords": ["train"],
            "hybrid_alpha": 0.5,
            "limit": 3
        },
        {
            "query": "What datasets were used for training?",
            "required_keywords": ["dataset", "training"],
            "similarity_threshold": 0.65,
            "hybrid_alpha": 0.4,
            "limit": 5
        }
    ]
    
    # Run tests for each search configuration
    for config in search_configs:
        print("\n" + "="*80)
        test_search(config)
        print("="*80) 