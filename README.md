# Gerogia Tech OMSCS: Summary of Course Difficulty and Rating

This project keeps an updated dashboard of Course Difficulty and Rating of Gatech OMSCS courses, deployed here: https://damianboh.github.io/omscs_courses_rating_difficulty.html

Explanatory Article here: https://medium.datadriveninvestor.com/use-python-to-analyze-georgia-tech-omscs-course-ratings-and-reviews-675a912aceed

A workflow is configured in GitHub actions to install necessary libraries from requirements.txt, run the Python script "update_page.py" that scrapes OMS Central website for course ratings and difficulty and generate the updated html page.

The html page is then pushed to my Github pages repository.

An accompanying Jupyter notebook "omscs_courses_rating_difficulty.ipynb" is included for exploration, it has similar code to the update_page.py script and shows the output at every step.
