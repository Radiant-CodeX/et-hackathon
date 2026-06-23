"""
The single place the AI model is configured.

LangChain is our orchestration framework; Azure AI Foundry is the model
provider. Person A owns this file. Person A imports `get_chat_response`;
Person C imports `llm` (and `embeddings`) to build chains, tools, and agents.

If USE_STUBS is true (default) or Azure is not configured, get_chat_response
returns a canned JSON-ish string so the whole app runs with no Azure key.
That keeps B, C, and D unblocked from Hour 0.

To swap to a non-OpenAI catalog model (Phi, Mistral, Llama) later, replace
AzureChatOpenAI with langchain's AzureAIChatCompletionsModel. Everything
built on `llm` keeps working unchanged.
"""
import config

llm = None
embeddings = None

if config.azure_configured():
    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

    llm = AzureChatOpenAI(
        azure_endpoint=config.AZURE_INFERENCE_ENDPOINT,
        api_key=config.AZURE_INFERENCE_KEY,
        api_version=config.AZURE_API_VERSION,
        azure_deployment=config.AZURE_DEPLOYMENT_NAME,
        temperature=0.2,
        max_tokens=1500,
    )

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=config.AZURE_INFERENCE_ENDPOINT,
        api_key=config.AZURE_INFERENCE_KEY,
        api_version=config.AZURE_API_VERSION,
        azure_deployment=config.AZURE_EMBEDDING_DEPLOYMENT,
    )


def get_chat_response(system: str, user: str, json_mode: bool = False) -> str:
    """Single-turn helper used by the ingestion pipeline (Person A)."""
    if config.USE_STUBS or llm is None:
        return _stub_response(system, user, json_mode)

    from langchain_core.messages import SystemMessage, HumanMessage

    model = llm
    if json_mode:
        model = llm.bind(response_format={"type": "json_object"})
    resp = model.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return resp.content


def _stub_response(system: str, user: str, json_mode: bool) -> str:
    """Canned extraction output so ingestion works with no Azure key."""
    if json_mode:
        return (
            '{"entities": ['
            '{"name": "Pump-01", "type": "Equipment", '
            '"metadata": {"location": "Bay 3"}},'
            '{"name": "Bearing wear", "type": "FailureMode", '
            '"metadata": {"severity": "high"}},'
            '{"name": "SKF", "type": "Supplier", "metadata": {}}'
            '], "relationships": ['
            '{"source": "Pump-01", "target": "Bearing wear", '
            '"type": "HAS_FAILURE_MODE"},'
            '{"source": "Pump-01", "target": "SKF", '
            '"type": "SUPPLIED_BY"}'
            ']}'
        )
    return "Stubbed AI response. Set USE_STUBS=false and configure Azure to enable real calls."
