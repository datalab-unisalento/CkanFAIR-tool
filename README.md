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

