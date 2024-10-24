# code-scanning-failures

## Project Description
`code-scanning-failures` is a script designed to scan GitHub repositories within an organization for code scanning analyses. It identifies and reports analyses with errors, providing a summary of the total analyses and errors by category for each repository.

## Features
- Scans all repositories within a specified GitHub organization.
- Reports the total number of analyses and the number of analyses with errors.
- Groups and counts errors by category.
- Handles GitHub API rate limiting.
- Provides detailed error messages for repositories with specific issues.

## Prerequisites
- Python 3.6 or higher
- GitHub Personal Access Token (PAT) with appropriate permissions

## Setup
1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/code-scanning-failures.git
   cd code-scanning-failures
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set the GitHub Personal Access Token (PAT):**
   ```sh
   export GITHUB_PAT=your_personal_access_token  # On Windows, use `set GITHUB_PAT=your_personal_access_token`
   ```

## Usage

1. **Run the script:**
   ```sh
   python main.py <org_name>
   ```
  Replace <org_name> with the name of your GitHub organization.

2. **Example:**
   ```sh
   python main.py your_org_name
   ```

## Output

The script will output the following information for each repository:

* Repository name
* Total number of analyses
* Number of analyses with errors
* Count of errors by category (if any)

## Error Handling
* The script handles GitHub API rate limiting by waiting for the rate limit to reset before retrying requests.
* If a repository requires Advanced Security to be enabled, the script will print an error message and continue with the next repository.

## Contributing
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
1. Create a new branch (`git checkout -b feature-branch`).
1. Make your changes.
1. Commit your changes (`git commit -m 'Add new feature'`).
1. Push to the branch (`git push origin feature-branch`).
1. Create a pull request.