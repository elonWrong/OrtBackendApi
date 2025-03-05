## Installation Guide

### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [python](https://python.org/) (version 10.x-12.x)

### Steps

1. **Clone the Repository**

   Clone the repository to your local machine using the following command:

   ```
   git clone https://github.com/elonWrong/OrtBackendApi.git
   cd OrtBackendApi
   ```

2. **Create and Activate Virtual Environment**

   Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**

    Navigate to the project directory and install the required dependencies:

   ```
   pip install requirements.txt
   ```

3. **Configure the Server**

   ```
   idk
   ```

4. **Run the Server**

   start the server in dev env:
   ```
   fastapi dev main.py
   ```

5. **To leave the Environment**

    ```
    deactivate
    ```

## Installation Guide

### Adding dependencies to the env

1. **Acticate your Virtual Environment**

    ```
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

2. **Install your desired Dependencies**

    ```
    pip install <the wanted dependencies>
    ``` 

3. **Add Dependencies to the requirement File**

    ```
    pip freeze > requirements.txt
    ```
