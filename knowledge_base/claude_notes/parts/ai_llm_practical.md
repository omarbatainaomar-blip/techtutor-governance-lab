<!-- topics: ai -->
# AI, Machine Learning and LLMs: Practical Notes

## AI, ML and deep learning: how the terms relate
Artificial intelligence is the broad goal of making machines do tasks that need intelligence. Machine learning is the part of AI where a system learns patterns from data instead of following hand-written rules. Deep learning is machine learning with neural networks that have many layers. Large language models are deep learning models trained on huge amounts of text to predict the next token.

## The standard ML workflow
Define the problem and the success metric. Collect and clean data. Split the data into training, validation and test sets. Pick a simple baseline first. Train, tune hyperparameters on the validation set, and evaluate once on the test set at the end. Deploy, then monitor, because data changes over time.
A typical split is 70 percent train, 15 percent validation, 15 percent test, but the right split depends on how much data you have.

## Data leakage
Data leakage means information from outside the training data, often from the test set or from the future, influences training, so the measured score is too optimistic. Common causes: scaling or imputing using statistics of the whole dataset before splitting, duplicates present in both train and test, and using a feature that would not be known at prediction time (for example, using the final outcome as a feature). The fix is to split first and fit every preprocessing step only on the training data, which scikit-learn pipelines make easy.

## Overfitting, underfitting and bias-variance
Underfitting: the model is too simple and performs badly on both training and validation data (high bias). Overfitting: the model memorises noise, so it scores very well on training data but poorly on new data (high variance).
Ways to reduce overfitting: more data, simpler model, regularisation (L1, L2, dropout), early stopping, data augmentation, cross-validation to detect it. Ways to reduce underfitting: more expressive model, better features, longer training, less regularisation.

## Classification metrics
Accuracy is the share of correct predictions and is misleading with imbalanced classes: a model that always predicts "no fraud" is 99 percent accurate when fraud is 1 percent of cases.
From the confusion matrix: precision is true positives divided by all predicted positives. Recall (also called sensitivity) is true positives divided by all actual positives. F1 is the harmonic mean of precision and recall. Choose by cost: for cancer screening favour recall (do not miss cases), for spam filters favour precision (do not block real mail).
ROC-AUC measures how well the model ranks positives above negatives across thresholds. For very imbalanced data, precision-recall curves are often more informative.
Regression metrics: MAE (mean absolute error), MSE and RMSE (penalise big errors more), and R squared.

## Cross-validation
In k-fold cross-validation the training data is split into k parts. The model is trained k times, each time using one part as validation and the rest for training, and the scores are averaged. It gives a more stable estimate than one split. Use stratified folds for classification so that class proportions stay the same.

## Gradient descent in plain words
Training means finding parameters that minimise a loss function. Gradient descent computes the slope (gradient) of the loss with respect to the parameters and moves the parameters a small step in the opposite direction. The step size is the learning rate. Too high and the loss jumps around or diverges. Too low and training is slow. Stochastic and mini-batch gradient descent use a small batch of examples per step, which is faster and adds helpful noise. Adam is a popular optimiser that adapts the step size per parameter.

## Neural network vocabulary
A neuron computes a weighted sum of inputs plus a bias and passes it through an activation function such as ReLU, sigmoid or tanh. Without non-linear activations a stack of layers collapses into one linear function. Backpropagation applies the chain rule to compute gradients for all layers efficiently. An epoch is one full pass over the training data. A batch is the group of examples used for one update.
Convolutional neural networks are strong on images because filters share weights across positions. Recurrent networks handled sequences before transformers. Transformers use attention, which lets every token look at every other token, and they train well in parallel.

## Tokens, embeddings and context windows
LLMs do not read characters or words directly. Text is split into tokens, which are pieces of words. English averages roughly 0.75 words per token, and Arabic often needs more tokens per word, so Arabic text uses up context faster.
An embedding is a vector of numbers that represents the meaning of a text. Texts with similar meaning have vectors that are close together, measured with cosine similarity. Multilingual embedding models place sentences with the same meaning in different languages near each other, which is why an Arabic question can retrieve an English passage.
The context window is the maximum number of tokens the model can consider at once, including the prompt, the retrieved passages and the answer.

## How an LLM generates text
The model outputs a probability for each possible next token, one token at a time. Temperature controls randomness: a low value gives more predictable output and a high value gives more varied output. Top-p sampling keeps only the smallest set of tokens whose probabilities add up to p. For factual question answering use a low temperature.

## Hallucination
A hallucination is a fluent answer that is not true or not supported by the source. It happens because the model predicts plausible text and has no built-in fact check. Ways to reduce it: ground the answer in retrieved documents, instruct the model to say when it does not know, ask for citations, lower the temperature, and verify important claims.

## RAG: retrieval-augmented generation
RAG gives an LLM relevant documents at question time. Steps: split documents into chunks, embed each chunk, store the vectors in a vector database, embed the user question, retrieve the nearest chunks, put them into the prompt, and ask the model to answer only from them.
Design choices that matter: chunk size (too small loses context, too large dilutes the match; 200 to 500 words is a common starting range), chunk overlap, keeping the heading with each chunk, how many chunks to retrieve (top-k), a similarity threshold below which the bot answers "I don't know", and metadata filters such as topic or language.
Hybrid search combines keyword search (BM25) with vector search and often beats either alone, especially for exact names, error codes and acronyms. A reranker is a second model that reorders the retrieved chunks by relevance and usually improves quality.
Typical failure modes: the right chunk was not retrieved (a retrieval problem, fix chunking or embeddings), the right chunk was retrieved but the model ignored it (a prompt or model problem), or the knowledge base simply lacks the answer (a coverage problem).

## RAG versus fine-tuning
RAG is best for adding facts that change or are private, and it can show sources. Fine-tuning is best for changing style, format or behaviour, or for teaching a narrow skill. It is a poor way to add knowledge that must stay up to date. Many systems use both.

## Prompt engineering basics
Be specific about the task, audience and output format. Give the role and rules in the system prompt. Provide one or two examples of the desired output (few-shot prompting). For reasoning tasks, ask the model to work step by step. Put the retrieved context clearly separated from the question. Tell the model what to do when the context is insufficient. Test prompts on a fixed set of questions instead of judging by one lucky answer.
Prompt injection is an attack where text inside a document or web page tries to give the model new instructions. Treat retrieved text as data, not as instructions, and do not give the model dangerous tools without checks.

## Evaluating a RAG chatbot
Build a test set of 30 to 100 questions with the expected answers and the expected source. Measure retrieval quality (was the right chunk in the top k, often called hit rate or recall at k) and answer quality (is it correct, complete and supported by the sources). Include questions that the knowledge base cannot answer, and check that the bot says so. Re-run the test set after every change to chunking, embeddings or prompts.

## Responsible AI
Models can reflect bias in their training data. Check performance across groups, not only overall. Do not feed private data to services you do not control. Be transparent that answers come from an AI, show sources, and let users report mistakes. For education, encourage students to verify and understand rather than copy.

## Python ML ecosystem map
NumPy for arrays. pandas for tables. matplotlib and seaborn for plots. scikit-learn for classic ML, pipelines and metrics. PyTorch and TensorFlow for deep learning. Hugging Face transformers for pretrained models. Jupyter notebooks for exploration. Ollama and llama.cpp run open models locally. ChromaDB, FAISS and pgvector store vectors.
