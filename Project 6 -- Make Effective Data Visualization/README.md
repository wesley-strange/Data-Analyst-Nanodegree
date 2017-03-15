SUMMARY

On April 15, 1912, the Titanic sank after colliding with an iceberg in the North Atlantic Ocean. More than 1,500 out of 2,224 passengers and crew on board were killed. One of the reasons for the huge loss of life was there were not enough lifeboats to accommodate all the people on board. The purpose of this visualization is to communicate to the reader that surviving the Titanic disaster was not just luck, but had a great deal to do with passenger demographics. This visualization hightlights the role passenger sex and class played in the survival odds.



DESIGN

Initial Design Decisions

	Chart type: 
		I created a 100% normalized bar chart so that the reader could easily compare the percentage of male passengers that survived versus female passengers. 

	Bar color choices: 
		I went with the default colors for the bars in the chart which happened to be red and blue. Reason being I did not know how to change the colors initially.

	Explanatory text:
		I added explanatory text to the bottom of the right column in the chart to help reinforce what the reader should be paying attention to - the difference in percentage of women that survived versus men. I thought the text helped the reader quickly understand the data in the chart. I chose to make the female percentage significantly larger than the males since I wanted the reader's focus to be on how large the female's percentage was compared to the male percentage. I also changed the font color to dark shade of blue and bolder to help direct the reader's attention to the text.

	Animation: 
		I added animation to the chart so the reader could see the data for each of the three passenger classes. The animation was ordered to start with the third class, then transition to the second class, and end with the first class. This order was used to visually show the reader that as the class increased from third to first, the percent of passengers that survived increased also. 

	Chart labels: 
		I added a chart title to the top-center of the graph to align with the website header. I also labeled the x and y axises appropriately. 

	Legend: 
		I added a legend to the top-right of the graph so the reader would understand what the red and blue colors meant. 

	Reader interaction: 
		I added interactive buttons below the chart after the initial animation so that the reader could continue to explore the data by the different Passenger Classes.


Design Changes Based on Feedback

	Reader feedback: “I see the values are in percentages, but is it possible to include number of passengers in this data as well so we know how many of the 2,224 were male/female & how many of each class survived/died?”
		Design change: I addressed this item by adding buttons to the visualization allowing the reader to toggle between percentage view and count view.

	Reader feedback: “My only question is where is this data from and how was it gathered?”
		Design change: I added the “About the data” section to inform the reader about the data and provided a link so the reader could find more information about the data.

	Reader feedback: “The only thing I don't really understand is why it still says ‘percentage of people’ on the vertical axis, even when you switch the data to number of people.”
		Design change: I updated the code to update the y-axis title when the reader toggles between the number of passengers and percentage of passengers views.

	Reader feedback: “I was confused on the view by percentages. It might be easier if the colors were different on that one. I thought blue was men and pink was women.”
		Design change: I moved the chart title and legend to the top-left position so that the reader encounters how to read the graph before they get to the data.

	Reader feedback: “I don’t understand why there isn’t more about why more women survived and more men died.”
		Design change: I didn’t make any updates to the graphic since I did not have this information readily available and it was not my intent to dig into the details to that level. 
		
	Reader feedback: "Confusing information in the tooltips. "Survived: 0" and "Survived: 1" represent whether a passenger survived or not - but this information is very confusing, especially when viewed with the absolute count. I'd suggest to either remove it or clarify what it represents."
		Design change: I set the tooltip to null since I couldn't figure out how to remove it completely.
		
	Reader feedback: "I'd suggest to iterate over the summary again and eventually express the (indeed astonishing!) findings more clearly, by fleshing out what "passenger demographics" means in this situation."
		Design change: Added one more sentence to the summary section to help clarify what the "passenger demographics" means in this example - "This visualization hightlights the role passenger sex and class played in the survival odds."

	Reader feedback: "Start both columns off empty and after clicking have the bars fill up through an animation. That would put movement and change into both columns and thus make them be considered more equally."
		Design change: I updated the visualization to start off the columns as empty and to show once the reader clicks the "Click to Start Animation" button.
	
	Reader feedback: "Also I would try to move the writing out of the column and place it above or underneath - for the same reason. Unless you consciously want to draw much more attention to the right column. However, if that was the case I would probably suggest to construct the visualization differently."
		Design change: I moved the explanatory text to the top right of the plot above the bar chart. I also added class identifier messages that flash briefly when the animation changes to let the reader know what passenger class the data is related to.

	Reader feedback: "Regarding the colors, you went ahead and addressed the comment of the viewer in a different way than they mentioned it. This can often be a good thing and effective, too. However it is also important to keep in mind what they were actually confused about (in this case the color choice) and reconsider why this choice was taken and whether there might be a better way to express it. E.g. often women - men are displayed using red - blue, so viewers are likely to interpret it like that. It would be possible to simply chose less "charged" colors, or even better: colors that are more correlated with death - survival. E.g. the deceased count could be encoded with gray, and the survived women in red, and men in blue - or simply one color for the survived population. If in contrast with gray, this could make the visualization even more intuitive and powerful."
		Design change: I updated the chart to use gray color for dead passengers and blue for survived passengers.



FEEDBACK

Reader 1 Feedback (1st Draft)

	What do you notice in the visualization?
		Very easy to follow & comprehend.

	What questions do you have about the data?
		I see the values are in percentages, but is it possible to include number of passengers in this data as well so we know how many of the 2,224 were male/female & how many of each class survived/died?

	What relationships do you notice?
		More woman survived than men & the higher the social class, the higher the percentage of survival (for both men & women).

	What do you think is the main takeaway from this visualization?
		It was good to be a first-class woman on April 15, 1912.

	Is there something you don’t understand in the graphic?
		Not in the graphic, that’s perfect, but in the paragraphs above, one sentence might be incomplete between the first & second paragraphs (“The people that survived…”).


Reader 2 Feedback (2nd Draft)

	What do you notice in the visualization?
		The biggest thing I noticed is how many people died in the wreck. The disparity between First, Second and Third class survivors is very noticeable. The amount of women that survived compared to men, show how important chivalry was in those days, as women and children were surely loaded into the boats before the men.

	What questions do you have about the data?
		My only question is where is this data from and how was it gathered?

	What relationships do you notice?
		The relationship between Class and survival stands out the most. The higher the class, the better the chance of survival. Also, a much higher percentage of women survived than men. If you were a woman in First Class, you had a great chance of survival.

	What do you think is the main takeaway from this visualization?
		To me the main takeaway is showing the correlation to class and sex, to the chances of surviving. It was obviously a benefit to be a wealthy woman on the Titanic. It also shows it was beneficial to be a wealthy male on the Titanic.

	Is there something you don’t understand in the graphic?
		The only thing I don't really understand is why it still says "percentage of people" on the vertical axis, even when you switch the data to number of people. I'm sure that's something minor, but I could see where it could throw some people off. Good work!


Reader 3 Feedback (2nd Draft)

	What do you notice in the visualization?
		I notice very few men survived and lots more women did. I like the graphs. They are very clear except I was confused on the view by percentages. It might be easier if the colors were different on that one. I thought blue was men and pink was women.

	What questions do you have about the data?
		Why did more men die? Why did more women live?

	What relationships do you notice?
		More women lived in every class.

	What do you think is the main takeaway from this visualization?
		I think the main take away is more lifeboats need to be available so more people would survive during this type of tragedy. I feel that women were given seats on the boat while men tried to float in the water dying of hypothermia.

	Is there something you don’t understand in the graphic?
		I don’t understand why there isn’t more about why more women survived and more men died.


Udacity Review 1 Feedback (3rd Draft)

	Confusing information in the tooltips. "Survived: 0" and "Survived: 1" represent whether a passenger survived or not - but this information is very confusing, especially when viewed with the absolute count. I'd suggest to either remove it or clarify what it represents.

	I'd suggest to iterate over the summary again and eventually express the (indeed astonishing!) findings more clearly, by fleshing out what "passenger demographics" means in this situation.
	
	Start both columns off empty and after clicking have the bars fill up through an animation. That would put movement and change into both columns and thus make them be considered more equally.
	
	Also I would try to move the writing out of the column and place it above or underneath - for the same reason. Unless you consciously want to draw much more attention to the right column. However, if that was the case I would probably suggest to construct the visualization differently.



RESOURCES

https://en.wikipedia.org/wiki/RMS_Titanic
https://github.com/PMSI-AlignAlytics/dimple/blob/master/src/objects/legend/methods/_getEntries.js
https://github.com/PMSI-AlignAlytics/dimple/blob/master/examples/advanced_storyboard_control.html
https://github.com/d3/d3-3.x-api-reference/blob/8a6827cee879765cf663fdd751187546688e9941/API-Reference.md
https://www.dashingd3js.com/svg-group-element-and-d3js
https://bl.ocks.org/mbostock/3886394
https://www.w3schools.com/colors/colors_shades.asp
https://www.w3schools.com/jsref/met_win_settimeout.asp
https://github.com/PMSI-AlignAlytics/dimple/tree/master/src/objects
https://www.w3.org/TR/SVG/styling.html
https://discussions.udacity.com/t/create-a-legend-for-a-dimple-plot-with-d3-js-lines-and-adding-series-to-a-dimple-plot/193070/18
https://www.w3schools.com/colors/colors_mixer.asp