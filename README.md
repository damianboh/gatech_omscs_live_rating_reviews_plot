# Gerogia Tech OMSCS: Summary of Course Difficulty and Rating

This project keeps an updated dashboard of stock sentiments in the Dow Jones Index, deployed here: https://damianboh.github.io/omscs_courses_rating_difficulty.html

A workflow is configured in GitHub actions to install necessary libraries from requirements.txt, run the Python script "update_page.py" that scrapes OMS Central website for course ratings and difficulty and generate the updated html page.

The html page is then pushed to my Github pages repository.

An accompanying Jupyter notebook "omscs_courses_rating_difficulty.ipynb" is included for exploration, it has similar code to the update_page.py script and shows the output at every step.
