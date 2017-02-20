# Predicting student performance based on Piazza student interaction network analysis
-------------------------------------------------------------------------------------------------------------------------
* Run main.py to generate networks from JSON files and get various statistics.

* piazza/data folder should look like this:
    *******************************
       ```
	piazza/data
	```
		
		course1
			fall11
				class_content.json
				users.json
			fall12
				class_content.json
				users.json
			summer13
				class_content.json
				users.json
			fall13
				class_content.json
				users.json
			spring15
				class_content.json
				users.json
			summer15
				class_content.json
				users.json
			fall16
				class_content.json
				users.json
		course2
			fall13
				class_content.json
				users.json
			spring15
				class_content.json
				users.json
	******************************

(where course1,course2,etc. are course names as defined in src/constants.py)
