# 🚗 AI Car Controller for TORCS using Neural Networks

This project is part of the final assignment for the AI 2002 course, focused on training an AI agent to control a racing car in TORCS (The Open Racing Car Simulator) using sensor telemetry and deep learning models.

## 📌 Project Overview

The objective is to develop an intelligent controller that can race competitively on different tracks using sensory inputs from the environment. Our controller leverages a neural network model trained on recorded telemetry data to output continuous control signals such as acceleration, braking, clutch, gear, and steering.

### Key features:

* Developed using Python and Keras/TensorFlow

* Uses telemetry-based sensor data for decision making

* Predicts 5 car controls: Acceleration, Braking, Clutch, Gear, and Steering

* Trained on real data extracted from TORCS runs

## 🧠 AI Model Architecture

* Input: 73 scaled telemetry features (e.g., speed, RPM, track sensor distances)

* Hidden Layers: Two Dense layers with 64 neurons and ReLU activation

* Output: 5 outputs with linear activation representing control values

* Optimizer: Adam with learning rate 0.001

* Loss Function: Mean Squared Error (MSE)

* Trained over 100 epochs with a batch size of 32

## 🧪 Dataset

The dataset (data.csv) contains sensor readings and control actions collected during car racing sessions in TORCS.

* Inputs (X): All telemetry features excluding the control actions

* Outputs (y): Control actions (Acceleration, Braking, Clutch, Gear, Steering)

Preprocessing includes:

* Scaling features using StandardScaler

* Splitting data into train/test sets (80/20)

* Dropping the "Gear" column during training for a simplified model

## 🏁 How to Run

### Required Python libraries:

* pandas

* numpy

* scikit-learn

* tensorflow

* Ensure data.csv is in the same directory as the notebook or script.

* Run the Jupyter Notebook AI_Car_Controller.ipynb to preprocess the data, train the model, and make predictions.

## 🎮 TORCS Integration

* We used the Python TORCS Client to interface with the TORCS simulation server.

* The controller receives telemetry via UDP and sends predicted control signals in response.

* The system runs in real-time with 20ms game ticks and a 10ms response window.

