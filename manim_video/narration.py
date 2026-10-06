"""Narration script for the layman-first video.  One scene -> list of segments (one spoken paragraph each).
Written for people with no statistics background: every idea gets a picture, an everyday comparison, then the precise name.
`python build_video.py tts` voices it; scenes pace themselves to the audio.  Paper numbers: see ../paper_values.py"""
NARRATION = {
 "A00_title": [
  "Imagine a crowd of dots on a page, and your job is to draw the one straight line that best describes them. Easy, until part of the crowd is misleading. This video builds, from scratch and with pictures, a clever way to find the right line anyway. It is called Rasher, spelled R A S h R, which stands for the repeated angular shorth. Do not worry about the name. By the end, every word in it will be a picture you can see in your head.",
 ],
 "A01_hook": [
  "Here are one hundred dots. Sixty-two of them follow a clear upward trend. The other thirty-eight sit in a tight little clump far away on the right, drifting downward.",
  "Ask a computer for the best line, and the classic method, called least squares, draws this grey line. It tilts down toward the clump. The majority says up, but the line says down.",
  "You might think the so-called robust methods, which were invented exactly to ignore bad points, would fix this. Two famous ones, called L M S and M M, draw the orange and purple lines. They also follow the clump, not the crowd.",
  "Now watch the new method. It draws this gold line, which follows the sixty-two points that actually agree with each other. The true slope here is two, and the new method finds two point zero two.",
  "We will go step by step. First, what a line even is, and why bad points break it. Second, the new idea, using directions between pairs of points. Third, why it works. And fourth, honest tests, including the cases where it does not help.",
 ],
 "A02_line_basics": [
  "Let us start at the very beginning. Suppose each dot is a student. Across is the number of hours studied, up is the exam score. A straight line through the dots is a summary: more hours, higher score.",
  "A line has two numbers. The first is the slope, which says how steep it is. Walk one step to the right. If the line climbs two steps, the slope is two. If it falls, the slope is negative. Flat means zero.",
  "The second number is the intercept. It is simply the height where the line crosses the vertical axis, the score you would predict for a student who studied zero hours.",
  "Together they give a recipe. Predicted score equals the intercept plus the slope times the hours. Finding the best line means finding the best two numbers. The whole video is about doing that when some of the dots are not honest.",
 ],
 "A03_best_line": [
  "But what makes a line the best? Real dots never sit exactly on a line. The vertical gap between a dot and the line is its miss, called a residual. A good line has small misses.",
  "The classic recipe, least squares, builds a real square on every miss and adds up their areas. Big misses make really big squares. The best line is the one that makes the total area of the squares as small as possible.",
  "Watch the line wiggle. When it is tilted badly, the squares are huge. When it settles along the dots, the squares shrink. The bottom of this wobble is the least squares line.",
  "Now the problem. A far-away dot with a big miss makes an enormous square, because squaring a big number makes it gigantic. The line swings toward that dot to shrink its square, like a seesaw with a heavy child at the far end.",
 ],
 "A04_crowds": [
  "We call a single strange dot an outlier. Statisticians have good tricks for a lone outlier. The trouble in our picture is different, because here thirty-eight dots are strange, and they are strange together.",
  "We call this coherent contamination. Think of an election. One person voting differently changes nothing. But a whole group that agrees with itself is a second opinion, and a method that merely counts misses can be fooled into following it.",
  "Our clump is also far out to the right. Far along the horizontal axis means the dots have long leverage, like a long handle on a lever, so they pull the line much harder than dots near the middle. People call this high leverage.",
 ],
 "A05_breakdown": [
  "Robust methods are judged by something called the breakdown point. Imagine replacing more and more honest dots by bad ones, placed as nastily as possible. The breakdown point is how many you can replace before the answer can be dragged anywhere at all.",
  "The ordinary average breaks with a single bad dot. Fancier methods survive nearly half the data being bad. That sounds like the end of the story. A method with fifty percent breakdown can never be dragged to infinity.",
  "But notice what that promise says. It says the line will stay somewhere reasonable. It does not say the line will follow the honest crowd. In our picture the robust lines stayed reasonable, and still chose the wrong crowd.",
 ],
 "A06_median_mad": [
  "Before the new idea we need two small tools that will come back later. The first is the median. Line the numbers up in order, and take the one in the middle. Here are seven numbers, and the middle one is the median.",
  "The average and the median usually agree. But now push one number to a million. The average explodes. The median does not even notice, because the middle person in a line barely changes when one person at the end runs away.",
  "The second tool measures typical spread. Take how far each number is from the median, then take the median of those distances. We call it the median absolute deviation. Think of it as the typical distance from the middle that a lone far-away number cannot spoil.",
  "To make it comparable with the usual standard deviation for bell-shaped data, we multiply it by one point four eight two six. We will call the result the robust scale. Median for the centre, robust scale for the size. Remember them.",
 ],
 "A07_residual_methods": [
  "Now let us see exactly how the famous robust methods go wrong. Take one of them, least median of squares. Its idea is neat: lay a ribbon along a candidate line, and make the ribbon as thin as possible while still covering half of all the dots.",
  "Around the true line, the ribbon has to be fairly wide, because the honest dots scatter a bit. A ribbon through the clump looks like a bad idea, because the dots are far from the honest crowd.",
  "But look at what the clump gives for free. It is nearly one single spot, so a thin ribbon through it already covers thirty-eight dots. To reach half the data it only needs twelve more, which it can pick up from the honest crowd by crossing it.",
  "Now slide the clump's share toward one half. The extra dots needed shrink to almost nothing, and the ribbon through the clump gets thinner and thinner, until it beats the honest line. This is the real reason these methods get attracted by a tight bad group.",
  "This is a mathematical fact for least median of squares. For the related methods, trimmed squares and M M, the same effect appears in experiments, but it is not proved.",
 ],
 "B01_pairs": [
  "So here is a different way to think. Forget candidate lines and misses. Pick just two dots and join them with a straight segment. A segment between two dots has a direction. We call such a segment a chord.",
  "Do this for every pair of dots. Here is a small crowd, where blue dots follow an upward trend and red dots form the clump.",
  "Look at the segments between two blue dots. They mostly lean upward, near the true trend. The segments between a blue and a red dot all lean the same other way, downward. And the segments between two red dots, which sit almost on top of each other, point every which way, but they are tiny.",
  "The honest trend shows up as a favourite direction among the chords. So perhaps we should not search for a line at all. We should find the direction that most chords agree on, and read the line off from it.",
 ],
 "B02_units": [
  "There is one catch. A direction depends on how we draw the axes. Look at these dots. If I stretch the vertical axis, the upward trend gets steeper. Squash it, and it flattens. Same dots, different angles, only because I changed the units.",
  "Imagine measuring height in metres on one axis and weight in grams on the other. The angle would change if you switched to kilometres. So before looking at directions we put both axes on equal footing.",
  "First, slide the data so that the median of each axis sits at zero. Second, divide each axis by its robust scale, the tool from before. Because both tools ignore far-away dots, the clump cannot spoil them.",
  "Now both axes are in the same measuring unit, the typical spread. We call the new coordinates u and v. Directions measured here will not change if someone redraws the original graph in different units.",
 ],
 "B03_angles": [
  "How do we measure a direction? With an angle, like a compass or a protractor. Stand at the start of a segment, face right, and turn upward until you face its other end. The turn, in degrees, is its angle.",
  "Why not just use the slope? Because slope breaks for near-vertical segments. A vertical segment has an infinite slope, and a nearly vertical one has a giant, unstable slope. An angle is calm: ninety degrees is vertical, and eighty-nine and ninety-one are close neighbours.",
  "Computers have a tool for this called atan two. Give it how far the segment goes up and how far it goes right, and it tells you which way the arrow points. You do not need the formula, only the idea: a direction is an arrow, and an arrow has an angle.",
 ],
 "B04_half_turn": [
  "One more subtlety. A line has no front and no back. An arrow pointing twenty degrees upward and an arrow pointing the exact opposite way, at two hundred twenty degrees, lie along the same line. So we only need angles from zero up to one hundred eighty.",
  "That makes a funny rule. Angles near zero and angles near one hundred eighty are almost the same direction. Five degrees and one hundred seventy-five degrees are nearly identical lines, only ten degrees apart, even though the numbers look far apart.",
  "Think of a clock that only has six hours, where after the last hour you wrap straight back to the first. Let us glue the two ends of the zero to one hundred eighty stretch together. Now it is a circle, with no ends at all.",
  "On this circle, to compare two directions, take the shorter way round. That distance is never more than ninety degrees. In the drawing we place each direction at double its angle, only so that the half-turn fills a full circle neatly. Remember: one dot on this circle is one direction of a line.",
 ],
 "B05_shorth": [
  "We now have a circle of directions, with a dot for every chord. We want the place where the dots pile up. The tool for that is the shorth, short for shortest half.",
  "Picture houses along a road, and we want the busiest neighbourhood. Slide a stretch of road along, always wide enough to include half of the houses. Of all those stretches, pick the shortest one. That is where the houses are most packed.",
  "Let us do it with twelve angles. Half of twelve is six, so every window must hold six angles. Slide it along, measure each width, and keep the narrowest. Its midpoint is the answer.",
  "Because directions live on a circle, a window may cross the seam between one hundred eighty and zero. To handle that, we copy the angles one more lap around, so a window can run on across the seam without a break.",
  "Why not the median angle instead? The median is the middle person in the line, and it is dragged toward stragglers. The shorth ignores the stragglers and goes to the crowd. Here a few scattered angles pull the median away, while the shorth stays in the middle of the real pile.",
 ],
 "B06_local": [
  "Now let us use this on our points. Pick one dot and call it the anchor. Draw its chords to every other dot, and mark all those directions on the circle. This is what the anchor sees when it looks around.",
  "Take an anchor from the honest crowd. Most of its chords go to other honest dots, and they pile up at one direction. The shortest half-window is narrow. The anchor's local direction is that midpoint, and the window's width tells how sure it is.",
  "Now take an anchor from the clump. Half of its chords go to its own neighbours in the clump, in all sorts of directions, and half go to honest dots. No narrow pile exists, so its window is wide, and its local opinion is weak.",
  "Do this for every dot. Each dot now gives one direction, its local opinion, together with a width that says how confident it is.",
 ],
 "B07_vote": [
  "We now have a hundred local opinions on the circle. This is where the word repeated comes in: apply the same idea again. Find the shortest window that holds half of the local opinions, and take its midpoint.",
  "Think of a committee. First every member consults everybody and forms a personal opinion. Then the committee itself finds the opinion that most members share. Two rounds of the same idea.",
  "The honest members form a big, tight group of opinions. The clump members, as we saw, have scattered opinions. The shortest half-window naturally sits on the honest group. The result is one final direction, called theta hat.",
  "Notice we never asked which line fits best. We only asked where the directions agree, once among chords, and once among local opinions.",
 ],
 "B08_back": [
  "We have a direction, but a direction is not yet a line on the original graph. First turn it into a slope. The slope of an arrow is its rise over its run, which is the tangent of the angle.",
  "Then undo the standardizing. We squeezed the axes, so we stretch the slope back: multiply by the vertical scale, divide by the horizontal scale. Now we have the slope on the original graph.",
  "For the height of the line, the intercept, let every dot make a suggestion. Given the slope, each dot says: the line should cross the vertical axis here. We take the median of those suggestions, the tool from before.",
  "And there is our line, gold, passing along the honest crowd and ignoring the clump. In this example the slope is two point zero two, against the true two.",
  "A fair warning. The intercept uses all dots, including the clump, so it can sit a little off even when the slope is right. The tests below measure the slope.",
 ],
 "B09_recap": [
  "Let us run the whole machine once more, in one breath. Standardize the axes. Draw the direction of every pair. Fold directions onto a circle, where a line has no front or back. For each dot, find the shortest half-window of its directions. That gives its local opinion.",
  "Then repeat: find the shortest half-window among the local opinions. Convert that direction into a slope, undo the standardizing, and take the median for the intercept. Every step is a picture: arrows, a circle, and a sliding window.",
  "Computing it takes a number of steps proportional to the number of dots squared, times a small logarithm, with no random guessing, so the same data always give the same line.",
 ],
 "C01_exact": [
  "Why should this work? Let us look at the best case first. Suppose all dots lie exactly on one line. Then every chord points the same way. Every dot's window has width zero, and the final direction is exactly that line.",
  "Now the stronger version. Keep the honest dots exactly on the line, and put fewer than half as many bad dots anywhere at all, as long as none sits on the line. Even the most mischievous placement cannot change the answer.",
  "Why? Because honest dots all agree exactly, so they form a perfect zero-width pile. A bad group smaller than half cannot make a pile of its own that is big enough to count. The perfect pile wins, always.",
 ],
 "C02_units": [
  "Second property. Change the units of the graph. Measure the horizontal axis in different units, or shift it. The method gives the same line, expressed in the new units, as it should.",
  "This works because standardizing removes shifts and rescaling, so the chords, the circle, and the windows are exactly the same. Only the last step, converting back, notices the new units.",
  "But a limit. If you tilt the picture, by adding a multiple of x to every y, the method can give a different answer than a plain tilt of its old answer. So it handles shifts and stretching, but not every possible distortion.",
 ],
 "C03_separation": [
  "The main theorem is about separation. Imagine the honest dots' directions forming a tight pile on the circle, and the bad dots' directions somewhere else. What if the honest pile is so tight that any window which touches even one bad direction, while still holding enough dots, is wider?",
  "Then the shortest window will never include a bad direction. And if the winning window never touches a bad direction, the bad directions cannot matter at all. You could remove them or move them around, and the winning window stays put.",
  "The method uses windows twice, so we need this at both stages. First among each honest dot's chords, and second among the local opinions. If both stages are separated, the final direction is decided by the honest dots only.",
  "Here is the experiment. We take the clump and slide it farther and farther along. The gold line, from this method, does not move at all once the clump is far enough. The other methods keep changing their minds.",
  "That is what the theorem says, and the experiment shows it: contamination that is separated has zero influence.",
  "Two honest caveats. The theorem assumes the median and scale from standardizing do not change, but those do use all the dots. And it states that separation holds. It does not say that separation always holds. The next tests ask when it does.",
 ],
 "C04_attraction": [
  "Now the other side of the coin. Why exactly do ribbon methods fail? Suppose a fraction of the dots, call it epsilon, sit at one single point, and the rest are honest, with some noise around a true line.",
  "A ribbon through that point has the whole fraction epsilon already inside. To cover half of the dots, it needs only a little more from the honest crowd. When epsilon is close to one half, that little more is almost nothing, so the ribbon can be extremely thin.",
  "A ribbon around the true line has to be fat enough to cover half of the dots just from the noisy honest crowd, and so it can never get as thin. So once epsilon is large enough, the ribbon criterion prefers the line through the bad point.",
  "This is a proven statement, but for least median of squares only. For the other robust methods, the experiments show the same effect, but no proof is claimed.",
 ],
 "C05_remark": [
  "A last point about what is really needed. You might think the method requires every honest chord to point near the true direction. That is too much to ask. Two honest dots that happen to sit almost above each other, with a little noise, give a chord that can point in nearly any direction.",
  "Here are such nearly vertical pairs, with wild directions. But they are only a few of the many pairs. Most chords still agree, and the shortest half-window finds that agreement.",
  "So what is needed is only that a half of the chords pile up, not all of them. This is exactly the kind of agreement that the shorth measures, and why the method can cope with noisy data.",
 ],
 "D01_experiments": [
  "Now the tests. The experiments use one hundred dots, spread along a line with some noise, and then replaced a fraction of them by bad dots. They tried three kinds of badness.",
  "The first is the compact clump we have been using, far to the right. The second is a competing line, a second honest-looking trend with a different slope. The third is a funnel: the honest dots get more scattered as we move right, and a second line is mixed in.",
  "For each situation they did sixty repetitions and counted the failures. A fit fails if its slope is off by more than one half. Failure counts, in percent, are what we will look at.",
 ],
 "D02_ordinary": [
  "First, the ordinary world: clean data, mild contamination, or a single bad kind of dot. Here the new method is not the winner.",
  "On perfectly clean data, the typical error of the slope is point zero three three for the new method, point zero two four for the M M method, and point zero two two for Ransack. On twenty percent vertical outliers, and on ten percent bad leverage, the M M method and Ransack are again slightly better.",
  "So if your data are mostly honest, use the established methods. They are more efficient there, and they are what everyone already trusts.",
 ],
 "D03_near_half": [
  "The new method shines when a big coherent group of bad dots, between about thirty-five and forty-six percent, competes with the honest crowd. Take the compact clump first.",
  "At thirty-six percent bad dots, the new method fails zero percent of the time. Least median of squares fails two percent, the trimmed squares and M M methods fail twenty-three percent, and Ransack fifty percent.",
  "At forty percent, the new method still fails zero percent. Least median of squares now fails fifty-eight, trimmed squares and M M fail every single time, and Ransack seventy-seven.",
  "At forty-four percent, the new method succeeds in forty percent of the experiments, while every competitor fails at least ninety-seven percent of the time. At forty-six percent, everything fails, including the new method.",
  "With a competing line, the new method has no failures all the way to forty-six percent, though Ransack stays strong and fails only twelve. With the funnel, the new method fails zero percent at forty, three at forty-four, and eight at forty-six.",
 ],
 "D04_limits": [
  "Now the limits, which matter as much as the wins. First, location. When the clump sits along the extension of the honest line, at about thirty degrees or equivalently minus one hundred fifty degrees, its chords point the same way as the honest chords. The two piles overlap and the separation is lost.",
  "In that case the new method fails seventy-eight and seventy-five percent of the time at the larger distance. The other methods also do badly. In ten of the twelve tested directions, the new method had no failures.",
  "Second, tightness. If the bad group is very tight, with spread zero point zero five, the new method never fails while least median of squares fails twenty-five percent and the others nearly always. But if the bad group is loose, with spread one or three, it is no longer a coherent clump, and all these methods do fine, with at most two percent failures.",
  "So the advantage belongs to compact, coherent, separated bad groups, not to just any outliers. And as we saw, beyond about forty-six percent nothing works.",
 ],
 "D05_wrap": [
  "Let us pull the story together. Ordinary methods ask which line has small misses, and a tight clump of bad dots can fool them. This method asks which direction the pairs of dots agree on, and it measures agreement with the shortest window holding half, twice.",
  "Use it when a large, tight, coherent group of dots disagrees with the honest majority, perhaps a third to a half of the data, and you want a repeatable, random-free answer. Prefer the classic methods for clean or lightly contaminated data.",
  "The deeper lesson is that robust does not simply mean safe. It matters what a method rewards. Rewarding small misses can reward the wrong crowd. Rewarding agreement of directions rewards the crowd that agrees.",
  "Thank you for watching. If a picture in this video helped, you now understand something many textbooks leave as formulas. Stay curious.",
 ],
}
