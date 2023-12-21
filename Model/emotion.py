# -*- coding: utf-8 -*-
"""emotion.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OSjYhZF5ivH-QTyj4R-IaKhZAYCoexrp
"""

import json
import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import re
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer        # module for stemming
import io
nltk.download('stopwords')
nltk.download('punkt')

from google.colab import drive
drive.mount('/content/drive')

data = pd.read_csv("/content/drive/MyDrive/ML Capstone Bangkit 2023H2/Data/emotion.csv")
data

empty_rows = data[data['Comment'].str.strip() == '']
data.drop(empty_rows.index)
data.dropna(inplace=True)
data.drop_duplicates(inplace=True)
data

data['Comment'] = data['Comment'].str.lower()

# Remove '/r/', other punctuation, hyperlinks, and hashtags
data['Comment'] = data['Comment'].str.replace(r'/r/|[^\w\s]|https?://\S+|www\.\S+|\#\w+', '', regex=True)

# Remove stopwords
stop_words = set(stopwords.words('indonesian'))
data['Comment'] = data['Comment'].apply(lambda text: ' '.join([word for word in word_tokenize(text) if word.lower() not in stop_words]))
data

from sklearn.model_selection import train_test_split

# Defining features and labels
X = data['Comment'].values
y = data['Emotion'].values

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# X_train dan y_train adalah data latih
# X_test dan y_test adalah data uji

le = LabelEncoder()
y_train = le.fit_transform(y_train)
y_test = le.fit_transform(y_test)

# Display the mapping between original labels and encoded values
label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))


print("Label Mapping:", label_mapping)

vocab_size = 10000
embedding_dim = 200
max_length = 200
trunc_type = 'post'
padding_type = 'post'
oov_tok = "<OOV>"

# Tokenization training data
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(X)

word_index = tokenizer.word_index

training_sequences = tokenizer.texts_to_sequences(X_train)
training_padded_sequences = pad_sequences(training_sequences, padding=padding_type, maxlen=max_length, truncating=trunc_type)

test_sequences = tokenizer.texts_to_sequences(X_test)
test_padded_sequences = pad_sequences(test_sequences, padding=padding_type, maxlen=max_length, truncating=trunc_type)

tokenizer_json = tokenizer.to_json()
with io.open('tokenizer_reddit.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(tokenizer_json, ensure_ascii=False))

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.GlobalMaxPooling1D(),
    tf.keras.layers.Dense(24, activation="relu"),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.summary()

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history = model.fit(training_padded_sequences, y_train, epochs=30, validation_data=(test_padded_sequences, y_test))

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Plot training and validation accuracy
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

model.save("model_emotion.h5")