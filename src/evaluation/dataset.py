"""
Evaluation Dataset: 10 Complex Multi-Hop Questions

Each question is designed to require information from at least two sources:
- Primary VectorDB (Wikipedia)
- Secondary VectorDB (ArXiv)
- Web Search (current information)
- SQL Database (AI model specifications)
"""

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "Which AI models released after 2020 have more than 100B parameters, and what transformer architecture improvements did they introduce?",
        "required_sources": ["SQL Database", "Wikipedia/ArXiv", "Web Search"],
        "expected_answer_contains": ["GPT-3", "parameters", "transformer", "attention"],
        "difficulty": "hard"
    },
    {
        "id": 2,
        "question": "How does the attention mechanism in transformers differ from RNNs, and which recent models use this mechanism?",
        "required_sources": ["Wikipedia", "ArXiv", "SQL Database"],
        "expected_answer_contains": ["self-attention", "RNN", "sequential", "parallel"],
        "difficulty": "medium"
    },
    {
        "id": 3,
        "question": "What are the key differences between GPT-3 and GPT-4 in terms of parameters and capabilities, and when were they released?",
        "required_sources": ["SQL Database", "Web Search"],
        "expected_answer_contains": ["GPT-3", "GPT-4", "175B", "parameters", "2020", "2023"],
        "difficulty": "medium"
    },
    {
        "id": 4,
        "question": "Explain the cross-attention mechanism in transformers and cite at least one research paper that introduced improvements to it.",
        "required_sources": ["Wikipedia", "ArXiv"],
        "expected_answer_contains": ["cross-attention", "encoder", "decoder", "query", "key", "value"],
        "difficulty": "hard"
    },
    {
        "id": 5,
        "question": "Which organizations have developed AI models with over 1 trillion parameters, and what benchmarks do these models achieve?",
        "required_sources": ["SQL Database", "Web Search"],
        "expected_answer_contains": ["trillion", "parameters", "benchmark"],
        "difficulty": "hard"
    },
    {
        "id": 6,
        "question": "What is BERT and how does its pre-training approach differ from GPT models? Include information about their release years.",
        "required_sources": ["Wikipedia", "SQL Database"],
        "expected_answer_contains": ["BERT", "GPT", "bidirectional", "masked", "autoregressive"],
        "difficulty": "medium"
    },
    {
        "id": 7,
        "question": "What are the latest developments in efficient transformer architectures as of 2024, and which models implement them?",
        "required_sources": ["ArXiv", "Web Search", "SQL Database"],
        "expected_answer_contains": ["efficient", "transformer", "2024"],
        "difficulty": "hard"
    },
    {
        "id": 8,
        "question": "How many parameters does Llama 2 have, and what makes it different from other large language models?",
        "required_sources": ["SQL Database", "Wikipedia", "Web Search"],
        "expected_answer_contains": ["Llama 2", "70B", "parameters", "open-source"],
        "difficulty": "easy"
    },
    {
        "id": 9,
        "question": "What is the relationship between model size (parameters) and performance on NLP benchmarks according to recent research?",
        "required_sources": ["ArXiv", "SQL Database"],
        "expected_answer_contains": ["parameters", "benchmark", "scaling", "performance"],
        "difficulty": "medium"
    },
    {
        "id": 10,
        "question": "Compare the architectures of Claude 3 and GPT-4: which one was released more recently and what are their key technical differences?",
        "required_sources": ["SQL Database", "Web Search"],
        "expected_answer_contains": ["Claude 3", "GPT-4", "2024", "2023"],
        "difficulty": "medium"
    }
]
