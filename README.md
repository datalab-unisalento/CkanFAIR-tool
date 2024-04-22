# CkanFAIR
ckanFAIR is a tool designed to assess the compliance of CKAN portals and their datasets with the core FAIR principles (Findable, Accessible, Interoperable, Reusable).

# Attention: Software Under Maintenance and Modification

## IMPORTANT NOTE: 
This repository refers to a prototype version of the ckanFAIR software. Currently, the software is offline while significant changes are being made. As it is a prototype, it may contain bugs that have already been resolved in the production version.

## Installation

To use ckanFAIR, follow these steps:

* Ensure you have Python installed on your system. You can download it from python.org.
* Download the tool's source code from the repository.
* Navigate to the directory of the tool in your terminal.
* Use pip to install the necessary dependencies listed in the requirements.txt file:
* Copy code
`pip install -r requirements.txt`

## Usage

The tool can be launched directly from the terminal without any arguments. Follow these steps to run the tool:

* Open the terminal on your system.
* Navigate to the directory where the tool was installed.
* Start the tool without any arguments:
* Copy code
`python ckanFAIR.py`
This will launch the tool and execute predefined actions without requiring additional arguments.

## Options

The tool does not require arguments for execution but offers configurable options within the source code.

## Configuring the Environment Variables
To configure the environment variables necessary for the tool to function properly, create a file named .env in the root directory of the project. In this file, specify the following parameters:

`TOOL_VERSION=alpha_v0.1
DATABASE_ENDPOINT=your_database_endpoint
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_PORT=your_database_port
DATABASE_NAME=your_database_name
CLOUD_FOLDER_ID=your_cloud_folder_id
CLOUD_SERVICE_ACCOUNT=your_cloud_service_account`

Ensure each parameter is assigned an appropriate value according to your setup. The TOOL_VERSION variable specifies the version of the tool, while the DATABASE_* variables configure the connection to the database, including the endpoint, username, password, port, and database name. Additionally, the CLOUD_FOLDER_ID variable identifies the folder ID of the cloud storage service utilized by the tool.

Lastly, for the CLOUD_SERVICE_ACCOUNT variable, you need to provide the service account credentials or token for authentication with the cloud service. This value may vary depending on the cloud provider and authentication method used.

Refer to your cloud service documentation for instructions on obtaining the service account credentials and ensure the .env file is correctly populated before running the tool.

Please replace "your_database_endpoint", "your_database_user", "your_database_password", "your_database_port", "your_database_name", "your_cloud_folder_id", and "your_cloud_service_account" with the actual values for your setup.

## Examples

The tool provides the ability to assess an entire CKAN instance or a single dataset. Follow the instructions provided within the tool for specific usage.

## Compatibility and Future Implementations

The tool is currently compatible only with the JSON response of a CKAN instance obtained through API.
We are actively working on implementing compatibility with reading the RDF of the dataset to enhance the functionality of the tool.

## Usage Context and Limitations

The tool is specifically designed for datasets from the public administration.
Some tests on fairness metrics are evaluated considering the nature of public administration data itself. Please note that the same reasoning may not be valid in other contexts.

## Customization Settings
The repository includes a settings modification system, enabling users to adapt the tool to their specific requirements and context. This system facilitates adjustments to various parameters directly within the tool's interface. Through the graphical user interface (GUI) provided, users can modify settings related to the format, permalink, properties, and vocabularies. Each tab within the GUI corresponds to a specific category of settings, offering intuitive control over the tool's behavior.

The format settings tab allows users to define and configure different data formats, specifying attributes such as point values, non-proprietary status, and machine readability. Additionally, the permalink settings tab provides options for managing permanent links associated with the tool's functionality.

Moreover, the properties settings tab enables users to define custom properties and their respective obligatory levels, ensuring compatibility with diverse datasets. Lastly, the vocabularies settings tab facilitates the management of vocabulary formats and properties, crucial for aligning the tool with specific data schemas and standards.

Please refer to the code provided for detailed implementation and usage instructions.
## Contributing

We are always open to suggestions, corrections, and new ideas! If you would like to contribute to this project, you can do so in several ways:

- Open a new issue to report bugs or propose new features.
- Submit a pull request with your changes.
- Contact us via email at [davidedamiano.colella@studenti.unisalento.it](mailto:davidedamiano.colella@studenti.unisalento.it) to discuss any suggestions or questions.

Please remember that this project is currently a prototype, and the software is undergoing maintenance and modifications. Your contributions and feedback are greatly appreciated as we continue to improve the software.

Thank you for your interest in contributing to this project!


## License

This project is released under the MIT License.

