<!-- topics: ai -->
# Neural Networks, Transformers and Training Explained in Depth

## From one neuron to a deep network
A single artificial neuron multiplies each input by a weight, adds the results together with a bias, and passes the sum through an activation function. A layer is many neurons that look at the same inputs. A deep network stacks layers so that each layer works with the features produced by the previous one: early layers detect simple patterns and later layers combine them into complex ones. In an image model the first layers react to edges, the middle layers to shapes and textures, and the last layers to whole objects.
The activation function is essential. If every layer were purely linear, a hundred layers would still be equivalent to one linear function, so the network could not learn curved decision boundaries. ReLU, which returns max(0, x), is the default choice in hidden layers because it is cheap and avoids saturating for positive values. Sigmoid squeezes values into 0 to 1 and is used for binary probabilities. Softmax turns a vector of scores into probabilities that add up to 1 and is used for multi-class outputs.
The number of learnable parameters grows quickly. A layer from 20 inputs to 64 outputs has 20 times 64 weights plus 64 biases, which is 1,344 parameters. Large language models have billions.

## What training really does
Training repeats four steps. The forward pass computes predictions from a batch of inputs. The loss function compares predictions with the true answers and produces one number that says how wrong the model is. The backward pass (backpropagation) uses the chain rule to compute the gradient, which says how the loss changes if each weight changes a little. The optimiser then moves every weight a small step in the direction that reduces the loss. One pass through the whole training set is an epoch.
For classification the standard loss is cross-entropy. A useful sanity check: before training, a model that guesses uniformly among C classes should have a loss near the natural log of C, so about 2.30 for 10 classes and about 1.10 for 3 classes. If your first loss is far from that value, there is probably a bug in the data pipeline or the loss setup.
Learning rate is the most important hyperparameter. If it is too high the loss oscillates or becomes NaN. If it is too low, learning is painfully slow. Common starting values are 1e-3 for Adam and 1e-2 to 1e-1 for plain SGD with momentum. Schedules that reduce the learning rate during training, and a short warm-up at the start, usually help.

## A minimal PyTorch training loop
```python
import torch
from torch import nn

model = nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, 3))
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):
    model.train()
    for x, y in train_loader:
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in val_loader:
            correct += (model(x).argmax(dim=1) == y).sum().item()
            total += y.numel()
    print(epoch, "val accuracy", correct / total)
```
Why each line exists: zero_grad clears old gradients, because PyTorch accumulates gradients by default. loss.backward computes the gradients, and optimizer.step updates the weights. model.train and model.eval switch layers such as dropout and batch normalisation between training and evaluation behaviour. torch.no_grad turns off gradient tracking during validation to save memory and time. CrossEntropyLoss expects raw scores (logits) and integer class labels, so do not add a softmax before it, which is a very common mistake.

## Debugging a network that does not learn
First try to overfit a single small batch of 10 to 20 examples. A healthy model and pipeline should reach almost zero loss on it within a few hundred steps. If it cannot, the problem is a bug, not a lack of data. Check that inputs and labels are aligned after shuffling, that data is normalised, that the loss matches the output layer, that the learning rate is sensible, and that you call zero_grad. Print the shapes of tensors at each step. Watch both training and validation loss: if training loss falls but validation loss rises, the model is overfitting, and you need regularisation, more data or a smaller model. If both stay high, the model is underfitting or the learning is broken.
Vanishing gradients happen when gradients shrink to almost zero as they pass back through many layers, so early layers stop learning. Remedies include ReLU-style activations, residual connections (used in ResNets and transformers), normalisation layers and careful weight initialisation. Exploding gradients are controlled by gradient clipping.

## Regularisation tools
Dropout randomly switches off a fraction of neurons during training so the network cannot rely on any single path. Weight decay (L2 regularisation) penalises large weights. Early stopping halts training when validation loss stops improving. Data augmentation creates modified copies of training examples, such as flipped or cropped images. Batch normalisation stabilises the distribution of layer inputs and usually allows higher learning rates. Layer normalisation does the same per example and is the standard in transformers.

## Convolutional and recurrent networks
A convolutional layer slides a small filter, for example 3 by 3, across an image. The same filter weights are reused at every position, so the layer needs far fewer parameters than a fully connected one and it detects a pattern wherever it appears. Pooling layers shrink the feature maps by summarising small regions. This is why convolutional networks were the standard for vision for a decade.
A recurrent network processes a sequence one step at a time and carries a hidden state forward as memory. Basic recurrent networks forget quickly because of vanishing gradients, and LSTM and GRU cells add gates that decide what to keep and what to forget. Recurrent models are slow to train because each step depends on the previous one, and that limitation is one of the reasons transformers replaced them for language.

## Attention: the core idea of transformers
When you read the sentence "The animal did not cross the street because it was too tired", you know that "it" refers to the animal. Attention lets a model do this kind of lookup. For every token the model computes three vectors by multiplying its embedding with learned matrices: a query (what am I looking for), a key (what do I contain) and a value (what information do I give). The score between two tokens is the dot product of the query of one with the key of the other. Scores are divided by the square root of the key dimension to keep them in a stable range, passed through softmax to become weights that sum to 1, and then used to take a weighted average of the value vectors.
The formula is softmax of (Q times K transposed divided by the square root of d_k), multiplied by V. The following code is a complete working version using NumPy.
```python
import numpy as np

def attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    scores = scores - scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores)
    weights = weights / weights.sum(axis=-1, keepdims=True)
    return weights @ V, weights
```
Subtracting the maximum before the exponential does not change the result but prevents numerical overflow. Every row of the weights matrix sums to 1. Multi-head attention runs several attention computations in parallel with different learned projections, so different heads can specialise, for example one in grammar relations and another in nearby words, and then concatenates the results.

## The transformer block and why it works
A transformer block has multi-head self-attention followed by a small feed-forward network applied to each token, with residual connections and layer normalisation around each part. Residual connections add the input of a sublayer to its output, which helps gradients flow through deep stacks. Blocks are repeated dozens of times. Because attention does not know word order by itself, position information is added: the original transformer used sinusoidal position encodings, and many current models use rotary position embeddings (RoPE).
Transformers are efficient to train because all tokens of a sequence are processed in parallel, unlike recurrent networks. The price is that attention compares every token with every other token, so the cost grows with the square of the sequence length. That is why very long contexts are expensive in time and memory. During generation, models store the keys and values of previous tokens in a KV cache so they do not recompute them, and this cache is a major part of memory use at long context lengths.

## Encoder, decoder and the model families
Encoder-only models such as BERT read the whole text at once with attention in both directions and are trained by predicting masked words. They produce good representations and are used for classification, search and embeddings. Decoder-only models such as the GPT family and most chat models use a causal mask, so each token can attend only to earlier tokens, and they are trained to predict the next token. They generate text one token at a time. Encoder-decoder models such as T5 read the input with an encoder and generate the output with a decoder, and they suit translation and summarisation.

## How a chat model is built
Pretraining on a huge text collection teaches the model language and a lot of world knowledge by next-token prediction. Supervised fine-tuning on examples of instructions and good answers teaches it to follow instructions and to hold a conversation. Preference tuning, such as reinforcement learning from human feedback or direct preference optimisation, pushes the model toward answers people rate as helpful and safe. The model itself has no live access to the internet or your files. Anything it knows after training must be supplied in the prompt, which is exactly what retrieval-augmented generation does.

## Tokenization
Models read tokens, not letters. Byte-pair encoding starts from small units and repeatedly merges the most frequent pairs, so common words become single tokens and rare words are split into several pieces. Text in languages that were less represented in the training data, Arabic included in many tokenizers, is often split into more tokens per word. That means the same content consumes more of the context window and costs more time. Numbers, code and unusual spellings also split into many tokens, which is one reason models can make arithmetic and spelling mistakes.

## Embedding models and similarity search
An embedding model is trained so that texts with similar meaning get vectors that are close together, usually with a contrastive objective that pulls related pairs together and pushes unrelated ones apart. Similarity is measured with cosine similarity, which is the dot product of two vectors divided by the product of their lengths. Cosine distance is one minus the cosine similarity, so smaller distances mean more similar texts. When vectors are normalised to length 1, cosine similarity equals the dot product.
```python
import numpy as np

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```
For example, the vectors [1, 0] and [1, 1] have cosine similarity of about 0.707. Multilingual models such as BGE-M3 map more than 100 languages into one shared space and accept long inputs, so an Arabic question and an English paragraph that answers it can be close to each other. Always use the same embedding model for documents and for queries, and re-embed everything if you change the model. Some models expect a prefix such as "query:" or "passage:", so read the model card.

## Fine-tuning, LoRA and quantization
Fine-tuning all parameters of a large model needs a lot of GPU memory. LoRA (low-rank adaptation) freezes the original weights and trains small added matrices, which can be only a fraction of one percent of the parameters, and the result is a small adapter file that can be attached to the base model. Fine-tuning is good for style, format and specialised behaviour, and a poor way of adding facts that change, for which retrieval is better.
Quantization stores weights with fewer bits. A rough memory estimate for the weights is the number of parameters times the bytes per parameter. A 7 billion parameter model needs about 14 GB in 16-bit precision, about 7 GB in 8-bit and about 3.5 to 4 GB in 4-bit, plus extra memory for the KV cache and runtime overhead. That is why 4-bit versions of 7B and 8B models run on ordinary laptops. Quantization lowers quality slightly, usually little at 8-bit and more noticeably below 4-bit.

## Running models locally with Ollama
Ollama runs open models on your own machine and exposes a local HTTP API on port 11434. Typical commands are ollama pull model to download, ollama run model to chat in the terminal, ollama list to see installed models and ollama serve to start the server if it is not already running. The API endpoint /api/chat takes a list of messages and /api/embed returns embeddings for one or more input texts. The default context length is modest, so for retrieval-augmented generation raise num_ctx in the request options when you send several long passages, otherwise the beginning of the prompt can be silently cut off. Smaller models answer faster but follow instructions and handle Arabic less reliably, so test with your own questions. If answers are slow, check whether the model fits in GPU memory, because spilling to the CPU makes generation much slower.

## Sampling settings in practice
Temperature rescales the probabilities before sampling. Near 0 the model almost always picks the most likely token, which is best for factual answers and code. Around 0.7 gives more varied, creative text. Top-p keeps only the most probable tokens whose combined probability reaches p, and top-k keeps only the k most probable. Repetition penalties reduce loops. For a question-answering assistant grounded in documents, use a low temperature such as 0.1 to 0.3.

## Reading papers and learning path
A practical order for learning: Python and NumPy, then pandas and basic statistics, then scikit-learn for classic models and evaluation, then a neural network from scratch on a tiny dataset, then PyTorch, then transformers with the Hugging Face library, then retrieval and building an application around a model. For each concept, implement the smallest possible version yourself, since writing attention or a training loop once by hand makes the library versions understandable.
