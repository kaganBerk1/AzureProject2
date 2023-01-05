from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    AnalyzeSentimentAction,
)

credential = AzureKeyCredential("463ff8058da5469eab2f41cb1e19bb46")
endpoint="https://myai1.cognitiveservices.azure.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = ["Microsoft was founded by Bill Gates and Paul Allen."]

poller = text_analytics_client.begin_analyze_actions(
    documents,
    display_name="Sample Text Analysis",
    actions=[
        RecognizeEntitiesAction(),
        AnalyzeSentimentAction()
    ]
)

# returns multiple actions results in the same order as the inputted actions
document_results = poller.result()
for doc, action_results in zip(documents, document_results):
    print(f"\nDocument text: {doc}")
    for result in action_results:
        if result.kind == "EntityRecognition":
            print("...Results of Recognize Entities Action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Confidence Score: {entity.confidence_score}")
                print(f".........Offset: {entity.offset}")

        elif result.kind == "SentimentAnalysis":
            print("...Results of Analyze Sentiment action:")
            print(f"......Overall sentiment: {result.sentiment}")
            print(f"......Scores: positive={result.confidence_scores.positive}; "
                  f"neutral={result.confidence_scores.neutral}; "
                  f"negative={result.confidence_scores.negative}\n")

        elif result.is_error is True:
            print(f"......Is an error with code '{result.code}' "
                  f"and message '{result.message}'")

    print("------------------------------------------")