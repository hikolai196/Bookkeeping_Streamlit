# Bookkeeping App README

---
## Introduction
This is an interactive Streamlit application designed for simple and efficient financial record management.
It provides a user-friendly interface to track income and expenses, visualize trends, and generate reports directly from CSV data files.
Ideal for individuals or small businesses looking for an intuitive bookkeeping solution without the complexity of traditional spreadsheets.

---
## Features
- Add, edit, and delete bookkeeping entries through a sidebar form
- Filter records by date range for focused analysis
- Visualize data with interactive charts (monthly expenses, category summaries, income vs. expenses)
- Download pivot tables for further analysis
- Color-coded categories for clear insights
- Recent entry management for quick edits and deletions
- Easy CSV file support for data portability and backup

---
## Installation

1. **Clone the Repository**
   
```bash
   git clone https://github.com/hikolai196/Bookkeeping_Streamlit.git
   cd Bookkeeping_Streamlit
```

2. Install Dependencies 
- Ensure you have pip installed. 
- Install required packages: 

   `pip3 install -r requirements.txt`

- Key dependencies: streamlit, pandas, plotly

--- 
## Running Your App

- Start the Streamlit app by running: 

   `streamlit run app.py`

- The app will open in your browser, providing access to all interactive features.

--- 
## Customization & CSV Management

- The app uses a CSV file (default: bookkeeping_data.csv) to store your records. 
- To switch datasets, change the filename in the code or upload a new CSV with the required columns:
Date, Category, Payment, Amount, Details -> - All changes (add, edit, delete) are saved automatically to the CSV file.

--- 
## Contributing
Contributions, bug reports, and suggestions are welcome! 
Please fork the repository and submit a pull request, or open an issue for discussion.

--- 
## License

This project is licensed under the MIT License. See the LICENSE file for details.

--- 
## Credits

- Developed by Yen-Ting "Hiko" Lai
- Inspired by practical bookkeeping needs and open-source community solutions
