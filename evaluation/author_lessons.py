"""Original authored foundation lessons. Regenerates lessons.json without AI calls."""
import json
from pathlib import Path

lessons = []
question_count = 0


def q(prompt, answer, other, explanation, hints, *, evidence=None, check=None):
    global question_count
    within = question_count % 4
    position = (question_count // 4 + within * 3) % 4
    options = list(other)
    options.insert(position, answer)
    result = dict(id=f'q{within+1}', kind='transfer' if within == 3 else 'practice', prompt=prompt,
                  options=options, answer_index=position, explanation=explanation, hints=hints)
    if evidence is not None:
        result['evidence'] = evidence
    if check is not None:
        result['check'] = check
    question_count += 1
    return result


def lesson(id, title, subject, age, skill, summary, explanation, example, visual, questions, passage=None):
    for question in questions:
        question['id'] = id + '-' + question['id']
    result = dict(id=id, title=title, subject=subject, age_band=age, skill=skill,
                  summary=summary, explanation=explanation, worked_example=example,
                  visual=visual, questions=questions,
                  encouragement='Take your time. You can use a hint, try again, or take a break.')
    if passage is not None:
        result['passage'] = passage
    lessons.append(result)


lesson('m68-01','Make ten, then add','maths','6-8','addition_within_20',
       'Use a group of ten to add small numbers.',
       'Adding joins groups. To add 8 and 5, move 2 from the group of 5 to the group of 8. Now you have 10 and 3. No counters were added or lost.',
       {'prompt':'What is 8 + 5?', 'explanation':'8 needs 2 to make 10. Split 5 into 2 and 3. Then 10 + 3 = 13.'},
       {'kind':'counters','groups':[8,5],'caption':'Eight counters and five counters can be regrouped into ten and three.'}, [
    q('What is 9 + 4?','13',['11','12','14'],'Give 1 from the 4 to the 9. Then 10 + 3 = 13.',
      ['How many does 9 need to make 10?','Split 4 into 1 and the part left over.','After making 10, add the remaining 3.'],check={'operation':'add','operands':[9,4]}),
    q('What is 7 + 5?','12',['10','11','13'],'7 needs 3 to make 10. There are 2 left from the 5, so the total is 12.',
      ['Try making a group of 10 first.','7 needs 3 more. How much of the 5 will remain?','You will have 10 and 2. Join those groups.'],check={'operation':'add','operands':[7,5]}),
    q('What is 6 + 7?','13',['12','14','15'],'Move 4 from 7 to 6. The groups become 10 and 3, which make 13.',
      ['Find how many 6 needs to reach 10.','Split 7 into 4 and 3.','Join the new group of 10 with the 3 left over.'],check={'operation':'add','operands':[6,7]}),
    q('A tray has 8 red beads and 6 blue beads. How many beads are there?','14',['12','13','15'],'Join 8 and 6. Use 2 to make 10, then add the 4 that remain: 14.',
      ['This story joins two groups.','8 needs 2 to make 10. Take those 2 from the 6.','There are 4 left to add to the group of 10.'],check={'operation':'add','operands':[8,6]}),
])

lesson('m68-02','Count equal groups','maths','6-8','equal_groups',
       'Count groups that all have the same number.',
       'Equal groups have the same amount in each group. Three groups of 2 have 2 + 2 + 2 items. Multiplication is a short way to write repeated equal groups: 3 × 2.',
       {'prompt':'There are 3 baskets with 2 apples in each. How many apples?', 'explanation':'Count 2, 4, 6. Three groups of 2 make 6 apples.'},
       {'kind':'counters','groups':[2,2,2],'caption':'Three equal groups. Each group has two counters.'}, [
    q('There are 2 boxes with 4 crayons in each. How many crayons?','8',['6','7','10'],'Two groups of 4 are 4 + 4 = 8.',
      ['Each box has the same number.','Count 4 for the first box, then 4 more.','You are finding 4 + 4.'],check={'operation':'multiply','operands':[2,4]}),
    q('There are 4 plates with 3 grapes on each. How many grapes?','12',['7','9','15'],'The four groups are 3 + 3 + 3 + 3 = 12.',
      ['Count one group for each plate.','Count in threes four times.','The first three counts are 3, 6, 9. Add one more group of 3.'],check={'operation':'multiply','operands':[4,3]}),
    q('There are 3 rows with 5 dots in each. How many dots?','15',['8','10','20'],'Three groups of 5 are 5 + 5 + 5 = 15.',
      ['The number in every row is 5.','Count in fives for three rows.','After two rows there are 10 dots. Add the last 5.'],check={'operation':'multiply','operands':[3,5]}),
    q('Five toy bikes each have 2 wheels. How many wheels are there?','10',['7','8','12'],'Five groups of 2 make 2 + 2 + 2 + 2 + 2 = 10 wheels.',
      ['Each bike is one group of 2 wheels.','Count in twos five times.','The first four counts are 2, 4, 6, 8. Count one more pair.'],check={'operation':'multiply','operands':[5,2]}),
])

lesson('m68-03','Share into equal parts','maths','6-8','halves_and_quarters',
       'Find one half or one quarter of a small group.',
       'A half is one of 2 equal parts. A quarter is one of 4 equal parts. The parts must be equal. When sharing counters, give one to each group in turn until none remain.',
       {'prompt':'Share 8 counters into 2 equal groups. How many in one half?', 'explanation':'Each group gets 4 counters. Both groups together still have 8. One half of 8 is 4.'},
       {'kind':'fraction','numerator':1,'denominator':2,'caption':'One of two equal parts is one half.'}, [
    q('What is one half of 6?','3',['2','4','6'],'Share 6 into 2 equal groups. Each group has 3.',
      ['A half means one of 2 equal groups.','Share the 6 counters equally between two groups.','Find a number that makes 6 when you add it to itself.'],check={'operation':'fraction','operator':'multiply','left':'6','right':'1/2'}),
    q('What is one quarter of 12?','3',['2','4','6'],'Share 12 into 4 equal groups. Each group has 3.',
      ['A quarter means one of 4 equal groups.','Give each group the same number of counters.','Four copies of the answer must make 12.'],check={'operation':'fraction','operator':'multiply','left':'12','right':'1/4'}),
    q('What is one half of 10?','5',['2','4','8'],'Two groups of 5 make 10. Each is one half.',
      ['You need 2 equal groups.','Count out 10 items and share them between the groups.','The answer plus itself must equal 10.'],check={'operation':'fraction','operator':'multiply','left':'10','right':'1/2'}),
    q('Eight paper stars are shared equally onto 4 cards. How many stars go on each card?','2',['3','4','6'],'Each card gets 2 stars. Four groups of 2 make 8.',
      ['There are 4 equal groups, one for each card.','Share one star to each card, then keep sharing.','Four copies of the answer must make 8.'],check={'operation':'fraction','operator':'multiply','left':'8','right':'1/4'}),
])

seed_passage='Mira put a seed in a pot. She added soil and gave it a little water. Every morning, she set the pot near a sunny window. For days, she saw only soil. Then a small green leaf appeared. Mira smiled and kept caring for the plant.'
lesson('r68-01','The patient seed','reading','6-8','details_and_simple_inference',
       'Find story details and use them to explain an idea.',
       'A detail is something the story tells you. To explain an idea about a character, look for what the character says or does. If you are unsure, read that part again.',
       {'prompt':'Where did Mira put the pot each morning?', 'explanation':'The story says she set it near a sunny window. Those words tell us the place.'},
       {'kind':'reading','focus':'Look for what Mira does.', 'caption':'Use the story’s words as clues.'}, [
    q('What appeared after several days?','A small green leaf',['A red flower','A new pot','A pile of stones'],'The story says a small green leaf appeared.',
      ['Look near the end of the story.','Find the sentence after Mira sees only soil.','What new green thing does that sentence name?'],evidence='Then a small green leaf appeared.'),
    q('What did Mira give the seed besides soil?','A little water',['A paper hat','A toy','A spoon of sand'],'Mira gave it a little water.',
      ['Read the second sentence.','Look for what she gave the seed.','The answer names something a plant can drink.'],evidence='She added soil and gave it a little water.'),
    q('Which action shows that Mira kept trying while she waited?','She cared for the pot every morning.',['She threw the pot away.','She forgot where the pot was.','She stopped after one day.'],'Mira returned every morning even when she could see only soil. That supports the idea that she was patient.',
      ['Find something Mira did more than once.','Look at the words “Every morning” and “For days”.','Choose the action that matches her daily care.'],evidence='Every morning, she set the pot near a sunny window.'),
    q('Read: “Oli tried tying a bow. It came loose. Oli tried again.” Which action shows that Oli kept trying?','Oli tried again.',['The bow came loose.','Oli found a plant.','Oli hid the string.'],'The words “Oli tried again” directly show another attempt.',
      ['Look for what Oli did after the bow came loose.','Which words describe another attempt?','Choose the action stated in the final sentence.'],evidence='Oli tried again.'),
],seed_passage)

book_passage='Sam could not find a library book. First, Sam looked inside a bag. The book was not there. Next, Sam checked under the bench and found it. Sam put the book in the bag. At the library, Sam returned it and said, “I am glad I checked the bench.”'
lesson('r68-02','The missing library book','reading','6-8','sequence',
       'Follow the order of events in a short story.',
       'Words such as first, next and then help us follow events. Ask what happened before and after each action. Keep the order the story gives you.',
       {'prompt':'Where did Sam look first?', 'explanation':'The word “First” comes before Sam looks inside the bag. That action happened before the bench search.'},
       {'kind':'reading','focus':'first → next → later','caption':'Follow the order of the story.'}, [
    q('Where did Sam find the book?','Under the bench',['Inside the bag','On a library shelf','Behind a tree'],'The story says Sam checked under the bench and found it.',
      ['Find the sentence with “found it”.','What place is named in that sentence?','It is the place Sam checked next, after the bag.'],evidence='Next, Sam checked under the bench and found it.'),
    q('What did Sam do just after finding the book?','Put it in the bag',['Look inside the bag','Return home','Ask for another book'],'The next sentence says Sam put the book in the bag.',
      ['Find the sentence right after the book is found.','What did Sam do with the book?','Choose the action before the trip to the library.'],evidence='Sam put the book in the bag.'),
    q('Which happened first?','Sam looked inside a bag.',['Sam checked the bench.','Sam returned the book.','Sam put the found book in the bag.'],'The story marks looking inside the bag with the word “First”.',
      ['Look for the word “First”.','Read the action in that sentence.','Choose the bag search, before the book was found.'],evidence='First, Sam looked inside a bag.'),
    q('Read: “First, Nia washed a cup. Next, Nia dried it. Then Nia put it away.” What happened just before the cup was put away?','Nia dried the cup.',['Nia washed the cup.','Nia bought the cup.','Nia filled the cup.'],'Drying comes just before putting away in the stated order.',
      ['There are three actions. Follow them in order.','Find the action between washing and putting away.','Look at the sentence that starts with “Next”.'],evidence='Next, Nia dried it.'),
],book_passage)

beetle_passage='A beetle stood beside a small puddle. Ishan watched it turn away from the water. He placed a wide leaf across the narrowest part of the puddle. The beetle walked over the leaf and reached dry ground. Ishan left the leaf there and walked on quietly.'
lesson('r68-03','A leaf bridge','reading','6-8','actions_and_inference',
       'Use actions in a story to support a sensible idea.',
       'Sometimes a story does not name a feeling or a quality. We can use actions as clues. Choose an idea the words support, rather than adding something that is not in the story.',
       {'prompt':'How did the beetle get across?', 'explanation':'It walked over the leaf. We know this because the story describes that action.'},
       {'kind':'reading','focus':'action → clue → idea','caption':'Explain your idea with a story clue.'}, [
    q('What did Ishan use as a bridge?','A wide leaf',['A long pencil','A small shoe','A piece of string'],'Ishan placed a wide leaf across the puddle.',
      ['Find what Ishan placed down.','Look for the object across the puddle.','The object came from a plant.'],evidence='He placed a wide leaf across the narrowest part of the puddle.'),
    q('Where did the beetle reach after crossing?','Dry ground',['A tree branch','A deep pond','Ishan’s bag'],'The story says the beetle reached dry ground.',
      ['Read what happened after the beetle walked over the leaf.','Find the place at the end of that sentence.','Choose the place without puddle water.'],evidence='The beetle walked over the leaf and reached dry ground.'),
    q('Which idea about Ishan is best supported?','He helped the beetle cross.',['He wanted to catch the beetle.','He was building a house.','He wanted to splash the beetle.'],'Placing the leaf gave the beetle a way to cross. Nothing says Ishan tried to catch or splash it.',
      ['Use what Ishan actually did.','What did his leaf allow the beetle to do?','Choose the idea connected to the beetle reaching dry ground.'],evidence='The beetle walked over the leaf and reached dry ground.'),
    q('Read: “A pencil rolled off Jo’s desk. Ren picked it up and handed it back.” Which idea is supported?','Ren helped Jo get the pencil back.',['Ren broke the pencil.','Jo gave Ren a present.','The pencil was blue.'],'Picking up and returning the pencil supports the idea of helping. The other details are not given.',
      ['Find the action Ren took.','What changed for Jo after that action?','Choose the idea supported by “handed it back”.'],evidence='Ren picked it up and handed it back.'),
],beetle_passage)

lesson('m911-01','Fractions with the same value','maths','9-11','equivalent_fractions',
       'Recognise equal amounts written as different fractions.',
       'Equivalent fractions name the same amount. Multiplying both the numerator and denominator by the same positive number keeps the value unchanged. For example, one half and two quarters cover the same amount of a whole.',
       {'prompt':'Write 1/2 using a denominator of 4.', 'explanation':'Multiply the numerator and denominator by 2: (1 × 2)/(2 × 2) = 2/4.'},
       {'kind':'fraction','numerator':2,'denominator':4,'caption':'Two of four equal parts cover one half of the whole.'}, [
    q('Which fraction has the same value as 2/3?','4/6',['2/6','3/4','4/3'],'Multiply both parts of 2/3 by 2 to get 4/6.',
      ['The numerator and denominator must change by the same factor.','Try multiplying both parts by 2.','The numerator becomes 4. What does the denominator become?'],check={'operation':'fraction','operator':'equivalent','left':'2/3'}),
    q('Which fraction has the same value as 3/4?','6/8',['3/8','4/6','6/4'],'Multiplying both 3 and 4 by 2 gives 6/8.',
      ['Keep the fraction’s value unchanged.','Look for the same multiplication applied to 3 and 4.','Doubling 3 gives 6; also double 4.'],check={'operation':'fraction','operator':'equivalent','left':'3/4'}),
    q('Which fraction has the same value as 3/9?','1/3',['1/9','3/6','2/3'],'Divide both parts by 3: 3/9 = 1/3.',
      ['You can also divide both parts by the same number.','Both 3 and 9 can be divided by 3.','Work out 3 ÷ 3 and 9 ÷ 3.'],check={'operation':'fraction','operator':'equivalent','left':'3/9'}),
    q('A strip has 5 equal parts and 2 are shaded. Each part is split into 3 smaller parts. What fraction is shaded now?','6/15',['2/15','6/5','3/15'],'There are 5 × 3 = 15 small parts in all, and 2 × 3 = 6 are shaded. The amount stays 2/5.',
      ['Both the shaded parts and all the parts are being split.','Multiply both 2 and 5 by 3.','Count the new shaded pieces and the new total pieces.'],check={'operation':'fraction','operator':'equivalent','left':'2/5'}),
])

lesson('m911-02','Walk around a rectangle','maths','9-11','perimeter',
       'Add the side lengths around the outside of a rectangle.',
       'Perimeter is the total distance around a shape. A rectangle has two equal lengths and two equal widths. Add all four sides, or calculate 2 × (length + width). Use units of length, such as centimetres.',
       {'prompt':'A rectangle is 6 cm long and 4 cm wide. What is its perimeter?', 'explanation':'6 + 4 + 6 + 4 = 20 cm. The area, 24 square centimetres, answers a different question.'},
       {'kind':'number_line','start':0,'end':20,'step':4,'caption':'Perimeter adds distances along all four sides.'}, [
    q('A rectangle is 7 cm long and 3 cm wide. What is its perimeter in cm?','20',['10','21','14'],'Add all four sides: 7 + 3 + 7 + 3 = 20 cm.',
      ['A rectangle has four sides.','There are two sides of 7 cm and two of 3 cm.','Double the sum of 7 and 3.'],check={'operation':'add','operands':[7,3,7,3]}),
    q('A rectangle is 5 m long and 2 m wide. What is its perimeter in m?','14',['7','10','12'],'The outside distance is 5 + 2 + 5 + 2 = 14 m.',
      ['You need the whole outside distance.','Do not stop after adding just one length and one width.','Find 2 × (5 + 2).'],check={'operation':'add','operands':[5,2,5,2]}),
    q('A square has sides of 6 cm. What is its perimeter in cm?','24',['12','18','36'],'A square has four equal sides, so 4 × 6 = 24 cm.',
      ['How many sides does a square have?','All four sides measure 6 cm.','Add four copies of 6.'],check={'operation':'multiply','operands':[4,6]}),
    q('A rectangular card is 9 cm by 4 cm. Ribbon goes once around its edge with no overlap. How many cm of ribbon are needed?','26',['13','18','36'],'Ribbon around the edge follows the perimeter: 9 + 4 + 9 + 4 = 26 cm.',
      ['“Around its edge” asks for perimeter.','Include both long sides and both short sides.','Calculate 2 × (9 + 4).'],check={'operation':'add','operands':[9,4,9,4]}),
])

lesson('m911-03','Find the missing number','maths','9-11','one_step_equations',
       'Use an opposite operation to find an unknown number.',
       'An equation says two values are equal. An unknown number can be called x. Undo addition with subtraction, subtraction with addition, and multiplication with division. Check by putting your answer back into the original equation.',
       {'prompt':'x + 6 = 15. What is x?', 'explanation':'Subtract 6 from both sides: x = 9. Check: 9 + 6 = 15.'},
       {'kind':'number_line','start':0,'end':24,'step':6,'caption':'Opposite operations can take you back to a missing number.'}, [
    q('x + 7 = 19. What is x?','12',['11','13','26'],'Subtract 7 from 19 to get 12. Check: 12 + 7 = 19.',
      ['Which operation undoes adding 7?','Subtract 7 from both sides.','Calculate 19 − 7, then check by adding 7.'],check={'operation':'equation','coefficient':'1','offset':'7','rhs':'19'}),
    q('3 × x = 24. What is x?','8',['6','7','21'],'Divide both sides by 3. 24 ÷ 3 = 8.',
      ['The unknown has been multiplied by 3.','Undo multiplication with division.','Find how many groups of 3 make 24.'],check={'operation':'equation','coefficient':'3','offset':'0','rhs':'24'}),
    q('x − 9 = 14. What is x?','23',['5','21','24'],'Add 9 to both sides. 14 + 9 = 23, and 23 − 9 = 14.',
      ['The original number became smaller by 9.','Add 9 to undo the subtraction.','Calculate 14 + 9.'],check={'operation':'equation','coefficient':'1','offset':'-9','rhs':'14'}),
    q('Four equal packs contain 36 cards altogether. How many cards are in each pack?','9',['8','12','32'],'If each pack contains x cards, 4 × x = 36. Divide 36 by 4 to get 9.',
      ['Let the number in one pack be x.','Four copies of x make 36.','Undo multiplying by 4 with division.'],check={'operation':'equation','coefficient':'4','offset':'0','rhs':'36'}),
])

rain_passage='The garden club set a rain gauge in an open patch of ground. On Monday, the gauge collected 4 millimetres of rain. On Tuesday, it collected 9 millimetres. Before each day’s reading began, the club emptied the gauge. Leela wrote the results in a table instead of relying on memory. “Two days tell us what happened on those days,” she said. “We need more observations to describe a usual week.”'
lesson('r911-01','The rain notebook','reading','9-11','facts_and_evidence',
       'Separate recorded facts from a claim that needs more evidence.',
       'A text may give measurements and explain what they support. Look for the exact time, place or group described. Avoid turning a small observation into a claim about every day or every place.',
       {'prompt':'Which day had the larger recorded amount of rain?', 'explanation':'Tuesday had 9 mm and Monday had 4 mm. The comparison is about those two recorded days.'},
       {'kind':'reading','focus':'measurement + time → supported claim','caption':'Keep your conclusion within the evidence.'}, [
    q('Why did the club empty the gauge before a new day’s reading?','To keep each day’s rain separate',['To make the next number larger','To stop all rain falling','To measure the soil colour'],'Emptying the gauge prevents yesterday’s collected rain from being included in the next day’s amount.',
      ['Think about what would happen if old rain stayed inside.','Each reading is meant to describe one day.','Choose the reason that keeps one day’s water separate from another’s.'],evidence='Before each day’s reading began, the club emptied the gauge.'),
    q('Which statement is directly supported by the recorded numbers?','Tuesday had more recorded rain than Monday.',['Tuesday is always the wettest day.','Every week gets 13 mm of rain.','The garden never needs watering.'],'The given numbers support a comparison of Monday and Tuesday, not a rule for all weeks.',
      ['Use only the two measurements in the text.','Compare 9 mm with 4 mm.','Avoid choices that say “always”, “every week” or “never”.'],evidence='On Tuesday, it collected 9 millimetres.'),
    q('Why does Leela want more observations?','Two days may not represent a usual week.',['She lost Monday’s number.','The table cannot hold numbers.','She knows it will never rain again.'],'Leela explicitly says more observations are needed to describe a usual week.',
      ['Read Leela’s final sentence.','She separates two recorded days from a usual week.','Choose the reason about how much evidence the claim needs.'],evidence='We need more observations to describe a usual week.'),
    q('Read: “At noon, one shady bench was cooler than one sunny bench.” Which conclusion stays within this evidence?','The shady bench was cooler at that noon check.',['All benches are coolest at noon.','Shade always makes every place cold.','Sunny benches can never be comfortable.'],'The observation compares two benches at one time. It does not establish a universal rule.',
      ['Notice the words “one” and “At noon”.','Keep the same benches and time in your conclusion.','Choose the statement about that check, rather than all places or times.'],evidence='At noon, one shady bench was cooler than one sunny bench.'),
],rain_passage)

map_passage='Asha and her uncle planned to walk to the museum across the footbridge. At the river, they found a sign: “Bridge closed for repairs.” Asha unfolded the map. She traced a second route along the river to the stone bridge, then back towards the museum. It was longer, so they would miss the first talk. “We can still see the afternoon display,” she said. They followed the new route without crossing the closed bridge.'
lesson('r911-02','A different route','reading','9-11','cause_and_inference',
       'Connect a character’s choices to clues in the story.',
       'To explain why an event happened, find its cause. To infer a character’s approach, use their words and actions together. A supported inference goes beyond a copied detail but still needs evidence.',
       {'prompt':'Why did Asha choose another route?', 'explanation':'The footbridge was closed for repairs. The sign explains why the original route could not be used.'},
       {'kind':'reading','focus':'cause → choice → result','caption':'Link a decision to the clue that explains it.'}, [
    q('What caused the change of route?','The footbridge was closed for repairs.',['The museum had moved.','Asha had lost the map.','The river had no bridges.'],'The closure sign explains why they changed their planned route.',
      ['Find the problem they discovered at the river.','Read the words on the sign.','Choose the detail that stopped the original plan.'],evidence='Bridge closed for repairs.'),
    q('In this story, what does “route” mean?','A way from one place to another',['A type of museum display','A repair tool','A river animal'],'Asha traces a route on a map so they can reach the museum by another way.',
      ['Look at what Asha traces on the map.','It goes along the river and across a bridge.','The word names the way they will travel.'],evidence='She traced a second route along the river to the stone bridge, then back towards the museum.'),
    q('Which idea about Asha is best supported?','She adjusts her plan when a problem appears.',['She refuses to change any plan.','She ignores the closure sign.','She no longer wants to visit the museum.'],'Asha finds another route and another display time rather than abandoning the visit or crossing the closed bridge.',
      ['Compare the first plan with Asha’s new plan.','Notice the new route and the afternoon display.','Choose the idea that includes adapting to the problem.'],evidence='We can still see the afternoon display'),
    q('Read: “The hall was being painted. Dev moved the group’s meeting to the courtyard and told everyone where to go.” Which inference is supported?','Dev found another way for the meeting to happen.',['Dev cancelled every future meeting.','Dev painted the hall alone.','Dev forgot to tell the group.'],'Moving the meeting and informing the group supports the idea of adapting the plan.',
      ['Identify the problem, then Dev’s action.','Did the action stop the meeting or allow another place?','Choose the idea supported by both moving and telling.'],evidence='Dev moved the group’s meeting to the courtyard and told everyone where to go.'),
],map_passage)

repair_passage='At the neighbourhood repair fair, volunteers worked at three tables. At one table, a torn backpack received a new patch. At another, a lamp worked again after a loose connection was repaired by a trained adult. At the last table, people learned to sew on buttons. A notice asked visitors to bring only items the volunteers could safely repair. By the end, several belongings were ready to be used again. The fair showed that some damaged things can be repaired instead of immediately replaced.'
lesson('r911-03','The repair fair','reading','9-11','main_idea_and_summary',
       'Choose a main idea that connects several details.',
       'A main idea tells what the whole text is mostly about. A useful summary keeps that main idea and a few important details. It should not exaggerate or focus on just one small example.',
       {'prompt':'Is the text mainly about the colour of a backpack?', 'explanation':'No colour is given. The backpack is one example of the wider idea: some belongings can be repaired and used again.'},
       {'kind':'reading','focus':'several details → one main idea','caption':'Choose an idea that fits the whole passage.'}, [
    q('Which statement best gives the main idea?','Some damaged belongings can be repaired and used again.',['Every broken item is safe to fix at home.','The fair was only about backpacks.','New things should never be bought.'],'The different tables all support repair and reuse. The passage limits this to some belongings and safe repairs.',
      ['Look for the idea connecting all three tables.','Keep the limit “some”; avoid “every” and “never”.','Choose the statement that includes both repair and using things again.'],evidence='The fair showed that some damaged things can be repaired instead of immediately replaced.'),
    q('Which detail best supports the idea of reuse?','Several belongings were ready to be used again.',['There were exactly three tables.','The fair had a notice.','A visitor counted the tables.'],'The detail about belongings being ready again directly shows reuse; merely counting tables does not.',
      ['Reuse means using something again.','Look for the outcome of the repairs.','Choose the sentence about what the belongings were ready for.'],evidence='By the end, several belongings were ready to be used again.'),
    q('Which summary keeps the important limit in the passage?','Volunteers repaired suitable items safely and taught a sewing skill.',['Everyone repaired electrical items without help.','Every damaged object was repaired.','The fair proved that replacement is always wrong.'],'The notice limited repairs to suitable items, and the lamp repair was done by a trained adult.',
      ['A summary should not claim more than the passage says.','Look at the safety notice and who repaired the lamp.','Choose the summary that keeps safe, suitable repairs.'],evidence='A notice asked visitors to bring only items the volunteers could safely repair.'),
    q('Read: “A class shared unused paper, refilled glue pots and reused display boards.” Which main idea connects all three actions?','The class found ways to use materials again.',['The class only made paper.','Every classroom item was broken.','The class stopped making displays.'],'Sharing, refilling and reusing all help existing materials be used rather than discarded.',
      ['Find what all three actions have in common.','Do not choose a detail that fits only one action.','Look for the idea of using existing materials again.'],evidence='A class shared unused paper, refilled glue pots and reused display boards.'),
],repair_passage)

lesson('m1215-01','Scale a ratio','maths','12-15','proportional_reasoning',
       'Keep a relationship constant while scaling quantities.',
       'A ratio compares quantities in a fixed order. If red:blue is 2:3, multiplying both quantities by the same positive factor preserves the ratio. Scaling only one quantity changes the relationship. Use a unit rate or scale factor to solve a proportion.',
       {'prompt':'A paint pattern uses red:blue beads in a 2:3 ratio. With 12 blue beads, how many red beads are needed?', 'explanation':'Blue scales from 3 to 12 by a factor of 4. Red must also scale by 4, giving 2 × 4 = 8.'},
       {'kind':'counters','groups':[2,3],'caption':'Keep the red-to-blue relationship while scaling both groups.'}, [
    q('Red:blue beads are in a 2:3 ratio. If there are 15 blue beads, how many red beads are needed?','10',['6','12','22'],'15 ÷ 3 = 5, so red must be 2 × 5 = 10.',
      ['Keep the order red:blue.', 'Find the factor that takes 3 blue beads to 15.', 'Apply that same factor to the 2 red beads.'],check={'operation':'ratio','known_base':3,'unknown_base':2,'known_value':15}),
    q('A drink uses concentrate:water in a 1:4 ratio. With 3 cups of concentrate, how many cups of water are needed?','12',['4','7','15'],'Concentrate scales by 3, so the water amount is 4 × 3 = 12 cups.',
      ['The second ratio number refers to water.','One cup of concentrate pairs with 4 cups of water.','Scale both quantities by the factor from 1 to 3.'],check={'operation':'ratio','known_base':1,'unknown_base':4,'known_value':3}),
    q('A map uses 2 cm for 5 km. How many km are represented by 6 cm?','15',['10','12','30'],'6 cm is three times 2 cm, so the distance is three times 5 km: 15 km.',
      ['Compare 6 cm with the map’s 2 cm unit.','Find the scale factor before changing the kilometres.','Multiply 5 km by that factor.'],check={'operation':'ratio','known_base':2,'unknown_base':5,'known_value':6}),
    q('Four identical notebooks cost 28 units of money. At the same price per notebook, what do 7 notebooks cost?','49',['31','42','56'],'Each notebook costs 28 ÷ 4 = 7 units. Seven notebooks cost 7 × 7 = 49 units.',
      ['The price per notebook stays constant.','Find the price of one notebook first.','Multiply that unit price by 7 notebooks.'],check={'operation':'ratio','known_base':4,'unknown_base':28,'known_value':7}),
])

lesson('m1215-02','Calculate with fractions','maths','12-15','fraction_arithmetic',
       'Use equal-sized parts to add or subtract fractions.',
       'For addition and subtraction, rewrite fractions with a common denominator so the parts have the same size. Add or subtract the numerators and keep that denominator. For multiplication, multiply numerators together and denominators together. Simplify when possible.',
       {'prompt':'What is 1/4 + 1/2?', 'explanation':'Rewrite 1/2 as 2/4. Then 1/4 + 2/4 = 3/4. The denominator stays 4 because the parts are quarters.'},
       {'kind':'fraction','numerator':3,'denominator':4,'caption':'One quarter plus two quarters makes three quarters.'}, [
    q('What is 1/3 + 1/6?','1/2',['2/9','1/9','2/3'],'1/3 = 2/6. Then 2/6 + 1/6 = 3/6 = 1/2.',
      ['Use a denominator that both fractions can share.','Rewrite one third as sixths.','Add the numerators of 2/6 and 1/6, then simplify.'],check={'operation':'fraction','operator':'add','left':'1/3','right':'1/6'}),
    q('What is 3/4 − 1/8?','5/8',['2/4','2/8','3/8'],'3/4 = 6/8. Subtracting 1/8 leaves 5/8.',
      ['Both amounts need the same-sized parts.','Rewrite three quarters as eighths.','Subtract one eighth from six eighths.'],check={'operation':'fraction','operator':'subtract','left':'3/4','right':'1/8'}),
    q('What is 2/3 × 3/5?','2/5',['5/8','6/8','2/15'],'Multiply to get 6/15, then divide numerator and denominator by 3 to get 2/5.',
      ['This is multiplication rather than addition.','Multiply the two numerators and the two denominators.','Simplify 6/15 by a factor shared by 6 and 15.'],check={'operation':'fraction','operator':'multiply','left':'2/3','right':'3/5'}),
    q('A jug holds 5/6 litre. You pour out 1/3 litre. How many litres remain?','1/2',['4/3','2/3','1/3'],'Rewrite 1/3 as 2/6. Then 5/6 − 2/6 = 3/6 = 1/2 litre.',
      ['Pouring out an amount means subtraction.','Write both amounts in sixths.','Subtract 2/6 from 5/6 and simplify.'],check={'operation':'fraction','operator':'subtract','left':'5/6','right':'1/3'}),
])

lesson('m1215-03','Undo two steps','maths','12-15','two_step_equations',
       'Keep an equation balanced while solving for an unknown.',
       'Apply the same operation to both sides of an equation. For a two-step equation, undo the last operation first. If a number is multiplied and then a constant is added, first subtract the constant, then divide. Substitute your answer to check it.',
       {'prompt':'Solve 4x + 2 = 18.', 'explanation':'Subtract 2 from both sides: 4x = 16. Divide both sides by 4: x = 4. Check: 4 × 4 + 2 = 18.'},
       {'kind':'number_line','start':0,'end':20,'step':5,'caption':'Undo the added amount, then undo multiplication.'}, [
    q('Solve 3x + 4 = 19. What is x?','5',['3','7','15'],'Subtract 4 to get 3x = 15, then divide by 3 to get x = 5.',
      ['Which operation happened after multiplying x by 3?','Undo the +4 on both sides first.','Once 3x = 15, divide both sides by 3.'],check={'operation':'equation','coefficient':'3','offset':'4','rhs':'19'}),
    q('Solve 2x − 5 = 9. What is x?','7',['2','4','14'],'Add 5 to both sides to get 2x = 14. Divide by 2 to get x = 7.',
      ['Undo subtracting 5 before dividing.','Add 5 to both sides.','Divide the resulting 14 by the coefficient 2.'],check={'operation':'equation','coefficient':'2','offset':'-5','rhs':'9'}),
    q('Solve x/4 + 2 = 5. What is x?','12',['3','7','20'],'Subtract 2 to get x/4 = 3. Multiply by 4 to get x = 12.',
      ['Undo the addition first.','After subtracting 2, x divided by 4 equals 3.','Undo dividing by 4 by multiplying both sides by 4.'],check={'operation':'equation','coefficient':'1/4','offset':'2','rhs':'5'}),
    q('A club pays a fixed 3-unit fee plus 5 units for each kit. The total is 23 units. How many kits were bought?','4',['3','5','20'],'Let x be the number of kits: 5x + 3 = 23. Subtract 3, then divide 20 by 5 to get 4 kits.',
      ['Separate the fixed fee from the cost of the kits.','Subtract the 3-unit fee from the total.','Divide the remaining cost by 5 units per kit.'],check={'operation':'equation','coefficient':'5','offset':'3','rhs':'23'}),
])

courtyard_passage='The student council considered two proposals for a bare courtyard: a shaded seating area or a mural wall. Supporters of seating counted 38 students standing during two lunch breaks because the existing benches were full. Mural supporters said a painting could reflect students’ ideas and make the space more welcoming. A cost estimate put seating above the current budget, but a local group offered some materials; the final cost was still unknown. The council agreed to check costs and ask a wider range of students before deciding. Neither proposal had been chosen.'
lesson('r1215-01','Two courtyard proposals','reading','12-15','claims_and_relevant_evidence',
       'Match evidence to a claim and notice what remains uncertain.',
       'Different kinds of evidence support different claims. A count may support a claim about use, while a cost estimate supports a claim about expense. An estimate is provisional. Do not confuse relevant evidence with a complete proof, or a proposal with an agreed decision.',
       {'prompt':'Does the count of standing students prove the seating is affordable?', 'explanation':'No. The count relates to a possible need for seating. Affordability requires reliable information about costs and the available budget.'},
       {'kind':'reading','focus':'claim → relevant evidence → limits','caption':'Separate usefulness, cost and the final decision.'}, [
    q('Which evidence most directly supports a possible need for more seating?','Students stood when the existing benches were full.',['The mural could reflect student ideas.','A local group offered some materials.','The council had not chosen a proposal.'],'Full benches and standing students relate directly to demand for seating, though the observations cover only two lunch breaks.',
      ['Identify the claim: a need for places to sit.','Which detail records how the current seats were used?','Choose the observation about full benches, rather than cost or appearance.'],evidence='Supporters of seating counted 38 students standing during two lunch breaks because the existing benches were full.'),
    q('What does “estimate” imply about the stated seating cost?','It is a provisional amount that may change.',['It is a guaranteed final payment.','It means the seating is free.','It means the budget is unlimited.'],'An estimate is an approximate assessment; the text also says the final cost was still unknown.',
      ['Read the information about final cost.','An estimate is different from a confirmed final total.','Choose the option that allows for change after more checking.'],evidence='the final cost was still unknown'),
    q('Which conclusion accurately describes the council’s position?','It wanted more information before choosing.',['It had rejected both proposals permanently.','It had already ordered the seats.','It had proved the mural was cheaper.'],'The council planned further cost checks and consultation, and the passage explicitly says neither proposal had been chosen.',
      ['Look at the final two sentences.','Separate planned investigation from a final decision.','Choose the statement that preserves the remaining uncertainty.'],evidence='The council agreed to check costs and ask a wider range of students before deciding.'),
    q('Read: “A club wants a larger room. On three occasions, every chair in its current room was occupied.” Which claim does this evidence most directly support?','The current seating was fully used on those occasions.',['A larger room will certainly be affordable.','Every student in the school attends the club.','The building has no other rooms.'],'The observation concerns chair use on three occasions. It does not provide costs, school-wide attendance or room availability.',
      ['Identify exactly what was observed.','Keep the claim about chairs and the three occasions.','Avoid conclusions needing evidence about money, all students or other rooms.'],evidence='On three occasions, every chair in its current room was occupied.'),
],courtyard_passage)

rehearsal_passage='After rehearsal, Anya held up her new sketch for the stage backdrop. Ravi looked at it briefly and turned towards a box of equipment without speaking. Anya folded the sketch, assuming he disliked it. A minute later, Ravi returned with a clamp. “The board is slipping,” he said. “Can we secure it before you show me the details?” Once the board was steady, he asked how Anya had chosen the colours. She unfolded the sketch again, noticing that she had mistaken a brief silence for a judgment.'
lesson('r1215-02','A silence at rehearsal','reading','12-15','perspective_and_inference',
       'Distinguish an observation from an interpretation.',
       'An observation describes what happened. An interpretation explains what it might mean. A character can interpret an action incorrectly. When new evidence appears, revise the interpretation rather than treating the first assumption as a fact.',
       {'prompt':'Is “Ravi disliked the sketch” an established fact at the start?', 'explanation':'No. Anya assumes this from a brief look and silence. Ravi later explains that he was concerned about the slipping board.'},
       {'kind':'reading','focus':'observation ≠ interpretation','caption':'Use later evidence to reconsider an early assumption.'}, [
    q('Which statement reports an observation rather than Anya’s interpretation?','Ravi turned towards a box without speaking.',['Ravi thought the sketch was terrible.','Ravi wanted Anya to stop drawing.','Ravi was jealous of the colours.'],'The turn and silence are described actions. The other choices add motives or opinions that the passage does not establish.',
      ['Look for an action someone could directly notice.','Separate what Ravi did from what he supposedly thought.','Choose the description of his movement and silence.'],evidence='Ravi looked at it briefly and turned towards a box of equipment without speaking.'),
    q('What new information best explains Ravi’s initial action?','He was concerned that the board was slipping.',['He had forgotten the rehearsal time.','He wanted to replace the sketch.','He had already left the building.'],'Ravi returns with a clamp and says the board is slipping, providing an alternative explanation for turning away.',
      ['Look at what Ravi brings back and says.','What problem would a clamp help address?','Choose the explanation connected to securing the board.'],evidence='The board is slipping'),
    q('How does Anya’s understanding change by the end?','She recognises that her first assumption lacked enough evidence.',['She becomes certain Ravi disliked the sketch.','She learns the board was never moving.','She decides questions about colour are insults.'],'Anya explicitly notices that she had mistaken silence for judgment after Ravi shows interest in the sketch.',
      ['Read the last sentence carefully.','Which earlier interpretation does she reconsider?','Choose the option about revising an unsupported assumption.'],evidence='she had mistaken a brief silence for a judgment'),
    q('Read: “Tao did not reply to a message. Later, Tao explained that the phone battery had run out.” Which statement separates observation from interpretation?','No reply was observed; deliberate ignoring was not established.',['No reply proves Tao was angry.','A flat battery proves every message was read.','The sender can know Tao’s thoughts.'],'Not replying is observed; the motive is uncertain. The later explanation provides a possible reason unrelated to deliberate ignoring.',
      ['What can the sender observe directly?','Does the absence of a reply reveal a person’s thoughts?','Choose the statement that avoids treating an assumed motive as fact.'],evidence='Later, Tao explained that the phone battery had run out.'),
],rehearsal_passage)

survey_passage='A lunch club asked 24 volunteers whether its weekly session should be longer. Twenty chose “longer” and four chose “keep the current length.” A draft newsletter headline read, “Students demand longer lunch breaks.” The editor changed it to “Most volunteers in the lunch-club survey prefer a longer club session.” She explained that the survey asked about one club session, not the whole lunch break, and the volunteers did not necessarily represent all students. The results could help the club plan, but they did not settle the school’s timetable.'
lesson('r1215-03','Read beyond the headline','reading','12-15','scope_and_generalisation',
       'Check whether a headline preserves a survey’s scope.',
       'A summary should keep the original group, question and level of certainty. Volunteers from one club may not represent everyone. Words such as all, demand and prove can make a claim stronger than the evidence allows.',
       {'prompt':'Why is “all students want longer lunch breaks” too strong?', 'explanation':'The survey involved 24 volunteers and asked about a club session. It did not ask every student or measure preferences about the entire lunch break.'},
       {'kind':'reading','focus':'who was asked + what was asked','caption':'Check the group and question before accepting a headline.'}, [
    q('What did the survey actually ask about?','The length of the lunch club’s weekly session',['The length of every school day','The cost of lunch','The entire school timetable'],'The question concerned the weekly club session, not the whole lunch break or timetable.',
      ['Read the first sentence.','Which particular activity might become longer?','Choose the club session rather than the wider school day.'],evidence='A lunch club asked 24 volunteers whether its weekly session should be longer.'),
    q('Why is “Students demand longer lunch breaks” misleading?', 'It changes both the surveyed group’s scope and the activity being discussed.', ['It correctly states that every student was asked.','It is wrong only because it has too few words.','It proves that no volunteer wanted a longer session.'],
      'The headline broadens volunteers to students in general and changes a club session into the whole lunch break. “Demand” also overstates a stated preference.',
      ['Compare the headline with the original question and group.','Look for a change from one club session to a whole break.','Also notice whether the volunteers can stand for all students.'],evidence='the survey asked about one club session, not the whole lunch break'),
    q('Which conclusion is directly supported by the numbers?','Most surveyed volunteers preferred a longer club session.',['All students preferred a longer lunch break.','No volunteer preferred the current length.','Exactly half wanted a longer club session.'],'Twenty of the 24 volunteers chose a longer club session, which is a majority of that surveyed group.',
      ['Keep the conclusion about the people who were actually surveyed.','Compare 20 with half of 24.','Choose “most surveyed volunteers”, not “all students”.'],evidence='Twenty chose “longer” and four chose “keep the current length.”'),
    q('Read: “Eight of ten volunteers from the swim club preferred an earlier pool session.” Which headline keeps the evidence’s scope?', 'Most surveyed swim-club volunteers prefer an earlier session.', ['The whole town demands an earlier school day.','All swimmers refuse the current timetable.','Nobody likes the pool’s current sessions.'],
      'The accurate headline keeps the surveyed volunteer group, the pool-session topic and the limited claim of a majority preference.',
      ['Keep the same group and the same activity.','Eight of ten supports “most”, not “all” or “nobody”.','Choose the headline about surveyed swim-club volunteers.'],evidence='Eight of ten volunteers from the swim club preferred an earlier pool session.'),
],survey_passage)

# V3 additions. The eighteen V2 lessons above remain unchanged.
lesson('m68-04','Take away, then check','maths','6-8','subtraction_within_20',
       'Find what remains when some items are taken away.',
       'Subtracting can tell us what is left. Start with the whole group and take away the stated amount. Check by joining what is left to what was taken away: you should get the starting amount.',
       {'prompt':'There are 12 shells. Move 3 aside. How many remain?', 'explanation':'Count back 3 from 12: 11, 10, 9. Check: 9 and 3 make 12.'},
       {'kind':'number_line','start':0,'end':15,'step':1,'caption':'A reference number line. Subtraction can be shown by counting back.'}, [
    q('What is 11 minus 4?','7',['6','8','15'],'Count back four steps from 11 to 7. Check: 7 + 4 = 11.',
      ['Start with 11 and take away 4.','Take away 1 to reach 10, then take away 3 more.','Count back three steps from 10.'],check={'operation':'subtract','left':11,'right':4}),
    q('What is 15 minus 6?','9',['8','10','11'],'Take away 5 to reach 10, then 1 more to reach 9.',
      ['Can you first reach 10?','Split the 6 into 5 and 1.','After taking away 5, take away the remaining 1.'],check={'operation':'subtract','left':15,'right':6}),
    q('What is 14 minus 7?','7',['6','8','9'],'Take away 4 to reach 10, then 3 more to reach 7.',
      ['First take away enough to reach 10.','The 7 can be split into 4 and 3.','You still need to subtract 3 from 10.'],check={'operation':'subtract','left':14,'right':7}),
    q('There are 16 seats. Six children sit down. How many seats are still empty?','10',['6','9','12'],'The empty seats are the 16 seats minus the 6 occupied seats: 10.',
      ['Separate the full group of seats from the occupied seats.','Take away the 6 seats that children use.','Find the number that makes 16 when 6 is added.'],check={'operation':'subtract','left':16,'right':6}),
])

lesson('m68-05','Tens and ones','maths','6-8','place_value_tens_ones',
       'Build two-digit numbers from tens and ones.',
       'A group of ten ones is one ten. In a two-digit number, the left digit counts tens and the right digit counts extra ones. Two tens and three ones make 20 + 3, or 23.',
       {'prompt':'What number is one ten and five ones?', 'explanation':'One ten is 10. Add the 5 ones: 10 + 5 = 15.'},
       {'kind':'counters','groups':[10,5],'caption':'One full group of ten and five extra ones make fifteen.'}, [
    q('What number is 2 tens and 4 ones?','24',['6','42','20'],'Two tens make 20. Four extra ones make 24.',
      ['Each ten is worth 10 ones.','Two tens make 20.','Join 20 and the 4 extra ones.'],check={'operation':'add','operands':[20,4]}),
    q('What number is 3 tens and 2 ones?','32',['5','23','30'],'Three tens make 30, then 2 more make 32.',
      ['Find the value of the tens first.','Three groups of ten make 30.','Add the two extra ones to 30.'],check={'operation':'add','operands':[30,2]}),
    q('What number is 4 tens and no extra ones?','40',['4','14','44'],'Four groups of ten make 40. Zero ones adds nothing.',
      ['No extra ones means add zero.','Four tens are 10 + 10 + 10 + 10.','Count by tens four times.'],check={'operation':'multiply','operands':[4,10]}),
    q('A box holds 5 bundles of 10 sticks and 3 loose sticks. How many sticks are there?','53',['8','35','50'],'Five bundles hold 50 sticks. Add 3 loose sticks to make 53.',
      ['Each bundle counts as one ten.','Five bundles make 50 sticks.','Add the loose sticks to the bundle total.'],check={'operation':'add','operands':[50,3]}),
])

context_passage='Asha found a tiny pebble. It was so small that it fitted on her fingertip. She put it in a shallow dish with only a little water. The dish was not deep. Asha gently placed a leaf beside it, moving slowly and carefully.'
lesson('r68-04','Words have neighbours','reading','6-8','vocabulary_in_context',
       'Use nearby words to understand an unfamiliar word.',
       'When a word is new, read the words around it. They may explain its meaning. Try a possible meaning in the sentence and check that it fits the story.',
       {'prompt':'What helps us understand the word tiny?', 'explanation':'The next sentence says the pebble was so small that it fitted on a fingertip. That clue tells us tiny means very small.'},
       {'kind':'reading','focus':'new word + nearby clue','caption':'Read around a word before choosing its meaning.'}, [
    q('What does tiny mean here?','Very small',['Very loud','Very hot','Very heavy'],'The pebble fits on a fingertip, so tiny means very small.',
      ['Read the sentence after tiny.','What does fitting on a fingertip tell you?','Choose a meaning about small size.'],evidence='It was so small that it fitted on her fingertip.'),
    q('What does shallow mean here?','Not deep',['Very wide','Full of ice','Bright red'],'The passage directly explains that the dish was not deep.',
      ['Look at the sentence after shallow dish.','Which words describe its depth?','Choose the meaning that matches not deep.'],evidence='The dish was not deep.'),
    q('What does gently mean here?','Slowly and carefully',['With a loud shout','In a hurry','With a hard push'],'The words after the action explain how Asha moves the leaf.',
      ['Read how Asha moved the leaf.','Find the words slowly and carefully.','Choose the meaning that matches that careful movement.'],evidence='moving slowly and carefully'),
    q('Read: "The path was narrow. Only one child could walk along it at a time." What does narrow mean?','Not wide',['Very noisy','Very wet','Not long'],'Only one child can fit across the path, so narrow refers to its small width.',
      ['Look at how many children can fit.','The clue is about space across the path.','Choose the meaning about width.'],evidence='Only one child could walk along it at a time.'),
],context_passage)

pronoun_passage='Mina picked up a kite. She carried it to the field. Two friends met Mina there. They helped hold the string. The kite rose above a tree. It had a yellow tail.'
lesson('r68-05','Who does the word mean?','reading','6-8','pronoun_references',
       'Connect words like she, they and it to the right person or thing.',
       'Writers use short words instead of repeating a name. She can refer to a person, they to people, and it to a thing. Look back and check which name makes sense in the sentence.',
       {'prompt':'Who does She mean in She carried it to the field?', 'explanation':'The sentence before names Mina. Mina is the person who picked up the kite, so She means Mina.'},
       {'kind':'reading','focus':'short word → person or thing','caption':'Read the earlier sentence to find a reference.'}, [
    q('In She carried it, who does She mean?','Mina',['The kite','A tree','The string'],'Mina is the named person who carries the kite.',
      ['Look at the person named just before She.','Who picked up the kite?','Try replacing She with Mina and read again.'],evidence='Mina picked up a kite. She carried it to the field.'),
    q('In They helped hold the string, who does They mean?','The two friends',['The kite and tree','The field','The yellow tail'],'The sentence before They introduces two friends.',
      ['Look at the sentence before They.','Which people have just arrived?','Replace They with the two friends to check.'],evidence='Two friends met Mina there. They helped hold the string.'),
    q('In It had a yellow tail, what does It mean?','The kite',['The field','The string','The tree'],'The kite is the thing described as rising and having a yellow tail.',
      ['Look for the thing that rose.','Which thing in this story has a tail?','Replace It with the kite to check the sentence.'],evidence='The kite rose above a tree. It had a yellow tail.'),
    q('Read: "Omar found a red ball. He put it in a box." What does it mean?','The red ball',['Omar','The box','A red kite'],'The ball is what Omar found and then put in the box.',
      ['Find the thing Omar picked up.','What could Omar put in the box?','Try replacing it with the red ball.'],evidence='Omar found a red ball. He put it in a box.'),
],pronoun_passage)

lesson('m911-04','Line up decimal places','maths','9-11','decimal_addition',
       'Add decimal amounts by matching place values.',
       'A decimal point separates whole units from parts. Line up decimal points so tenths join tenths and hundredths join hundredths. You can add a zero at the end of a decimal without changing its value: 1.2 and 1.20 are equal.',
       {'prompt':'What is 1.2 + 0.35?', 'explanation':'Write 1.20 + 0.35. Twenty hundredths and thirty-five hundredths make fifty-five hundredths. The total is 1.55.'},
       {'kind':'fraction','numerator':3,'denominator':10,'caption':'Three tenths of a whole is 0.3. Match parts of equal size when adding.'}, [
    q('What is 0.4 + 0.35?','0.75',['0.39','0.435','0.70'],'Write 0.40 + 0.35. Forty plus thirty-five hundredths is seventy-five hundredths.',
      ['Match hundredths with hundredths.','Write 0.4 as 0.40.','Add 40 hundredths and 35 hundredths.'],check={'operation':'add','operands':['0.4','0.35']}),
    q('What is 2.65 + 1.2?','3.85',['2.77','3.67','4.05'],'Write 1.2 as 1.20. Then 2.65 + 1.20 = 3.85.',
      ['The decimal points need to line up.','Write the second number as 1.20.','Join the whole units and then the hundredths.'],check={'operation':'add','operands':['2.65','1.2']}),
    q('What is 0.85 + 0.3?','1.15',['0.88','0.115','1.05'],'Eighty-five plus thirty hundredths is 115 hundredths, which is 1.15.',
      ['Write both amounts in hundredths.','Add 85 hundredths and 30 hundredths.','One hundred hundredths make one whole.'],check={'operation':'add','operands':['0.85','0.3']}),
    q('A ribbon is 1.75 metres long. Another is 0.6 metres long. What is their combined length in metres?','2.35',['1.81','2.05','7.75'],'The combined length is 1.75 + 0.60 = 2.35 metres.',
      ['Combined length means add the two lengths.','Write 0.6 as 0.60 before adding.','Add the hundredths, carrying one whole if needed.'],check={'operation':'add','operands':['1.75','0.6']}),
])

lesson('m911-05','Count minutes between times','maths','9-11','elapsed_time',
       'Find a duration by counting minutes across an hour.',
       'An hour has 60 minutes. To find a duration, count from the start time to the next full hour, then from there to the end time. Add those parts. A clock time is not a decimal number.',
       {'prompt':'How many minutes pass from 2:45 pm to 3:10 pm?', 'explanation':'From 2:45 to 3:00 is 15 minutes. From 3:00 to 3:10 is 10 minutes. Together that is 25 minutes.'},
       {'kind':'number_line','start':0,'end':60,'step':10,'caption':'One hour contains sixty minutes. This is a duration scale, not a clock.'}, [
    q('How many minutes pass from 9:40 am to 10:05 am on the same day?','25',['35','45','65'],'It is 20 minutes to 10:00, then 5 more: 25 minutes.',
      ['Count to the next full hour first.','From 9:40 to 10:00 is 20 minutes.','Add the 5 minutes after 10:00.'],check={'operation':'add','operands':[20,5]}),
    q('How many minutes pass from 1:50 pm to 2:30 pm on the same day?','40',['20','30','80'],'Ten minutes reach 2:00, then 30 more reach 2:30: 40 in total.',
      ['Split the time at 2:00.','There are 10 minutes before 2:00 and 30 after.','Join the two durations.'],check={'operation':'add','operands':[10,30]}),
    q('How many minutes pass from 11:15 am to 12:00 noon?','45',['15','35','85'],'A full hour has 60 minutes. Fifteen have passed, so 60 minus 15 remain.',
      ['The end time is the next full hour.','Use 60 minutes for the whole hour.','Subtract the first 15 minutes from 60.'],check={'operation':'subtract','left':60,'right':15}),
    q('A bus leaves at 4:35 pm and arrives at 5:20 pm the same day. How long is the trip in minutes?','45',['35','55','85'],'It takes 25 minutes to reach 5:00 and 20 more to reach 5:20, giving 45.',
      ['Divide the trip at 5:00.','Find the minutes from 4:35 to 5:00.','Add that 25-minute part to the 20-minute part.'],check={'operation':'add','operands':[25,20]}),
])

accounts_passage='Lena wrote: "At the pond, I counted three ducks beside the bridge. I watched them paddle towards the reeds. The wind made it hard to hear the guide." Arun wrote: "I stood beside Lena at the pond. Three ducks swam towards the reeds. I noticed a dragonfly on the bridge rail. The guide used a picture card to explain the pond insects." Both accounts describe the same visit, but each writer includes different details.'
lesson('r911-04','Two accounts of one visit','reading','9-11','comparing_accounts',
       'Find shared details and differences without inventing a disagreement.',
       'Two people can describe the same event differently. A shared detail appears in both accounts. A detail mentioned in only one account is not automatically a contradiction: the other writer may simply have left it out.',
       {'prompt':'Does Lena say that there was no dragonfly?', 'explanation':'No. Lena does not mention a dragonfly. Missing a detail is different from denying it.'},
       {'kind':'reading','focus':'shared detail | extra detail | contradiction','caption':'Check what each writer actually says.'}, [
    q('Which detail appears in both accounts?','Three ducks moved towards the reeds.',['A dragonfly rested on the rail.','The wind made hearing difficult.','The guide used a picture card.'],'Both writers describe three ducks heading towards the reeds.',
      ['Read the sentences about the ducks in each account.','Look for matching number and movement.','Choose a detail both writers include.'],evidence='Three ducks swam towards the reeds.'),
    q('Which detail is included only by Arun?','A dragonfly was on the bridge rail.',['There were three ducks.','The ducks moved towards the reeds.','The visit was at a pond.'],'Arun names the dragonfly; Lena does not mention it.',
      ['Compare Arun’s extra observations with Lena’s account.','Find an insect named in only one account.','Choose the observation about the bridge rail.'],evidence='I noticed a dragonfly on the bridge rail.'),
    q('What can we conclude from Lena not mentioning the picture card?','Her account leaves out that detail.',['She proves that no card was used.','Arun must have invented the guide.','They visited different ponds.'],'An omitted detail does not prove the event did not happen.',
      ['Does Lena deny that the guide used a card?','Distinguish not mentioning from saying it did not happen.','Choose the conclusion that stays within the written accounts.'],evidence='each writer includes different details'),
    q('Read: "Bo wrote: We heard a bell at the station. Inez wrote: At the station, a bell rang and a porter waved." Which detail is shared?','A bell sounded at the station.',['A porter waved.','A train was late.','The station was empty.'],'Both accounts report the bell; only Inez mentions the porter.',
      ['Find an event named by both Bo and Inez.','Heard a bell and a bell rang describe the same event.','Leave out the extra action only Inez reports.'],evidence='At the station, a bell rang'),
],accounts_passage)

instructions_passage='The class library has these borrowing instructions: Choose one book and write its title on your borrowing card. Before leaving, show the book and card to the librarian. You may keep the book for seven days. To keep it longer, ask the librarian before the return date. If a page is damaged, tell the librarian; do not try to repair it yourself. Return the book to the labelled return box, not directly to a shelf.'
lesson('r911-05','Read instructions carefully','reading','9-11','instructions_and_conditions',
       'Notice required actions, conditions and exceptions in a short guide.',
       'Instructions tell a reader what to do. Words such as before and if add conditions. Read the entire instruction before deciding an action, and keep permissions separate from requirements.',
       {'prompt':'May a borrower simply decide to keep a book for another week?', 'explanation':'The guide says to ask the librarian before the return date. Wanting more time does not itself give permission.'},
       {'kind':'reading','focus':'action + condition + timing','caption':'Look for before, if and other words that limit an instruction.'}, [
    q('What must a borrower do before leaving with a book?','Show the book and card to the librarian.',['Put the book straight on a shelf.','Choose three books.','Repair every loose page.'],'The instructions explicitly require showing both items before leaving.',
      ['Find the words Before leaving.','Read which two items must be shown.','Choose the action involving the librarian and both items.'],evidence='Before leaving, show the book and card to the librarian.'),
    q('What should a borrower do after noticing a damaged page?','Tell the librarian.',['Repair it without asking.','Hide the damage.','Leave the book outdoors.'],'The guide says to tell the librarian and not attempt a repair.',
      ['Look for the instruction beginning If.','What action follows the damaged-page condition?','Choose reporting the problem rather than fixing it yourself.'],evidence='If a page is damaged, tell the librarian; do not try to repair it yourself.'),
    q('Where should a borrowed book be returned?','The labelled return box',['Any empty shelf','The borrowing card drawer','The nearest desk'],'The final instruction names the return box and rules out returning straight to a shelf.',
      ['Read the final sentence.','Which place is named after Return the book?','Choose the labelled box, not a shelf.'],evidence='Return the book to the labelled return box, not directly to a shelf.'),
    q('Read: "To use the art room after lunch, sign the list before noon. If the list is full, ask the teacher about another day." What should someone do when the list is full?','Ask the teacher about another day.',['Add a name over another person’s.','Enter the room without signing.','Assume the room is always closed.'],'The condition about a full list has a specific next action: ask the teacher about another day.',
      ['Find the instruction beginning If.','Match the full-list condition to its stated action.','Choose asking about another day.'],evidence='If the list is full, ask the teacher about another day.'),
],instructions_passage)

lesson('m1215-04','Percentages as parts of a whole','maths','12-15','percentages_of_amounts',
       'Calculate a percentage amount and distinguish it from the remaining total.',
       'Percent means per hundred. Convert a percentage to a fraction out of 100, then multiply by the whole amount. Check what the question asks: a discount amount is different from the price after the discount.',
       {'prompt':'What is 25 percent of 80?', 'explanation':'25/100 is one quarter. One quarter of 80 is 20. This is the percentage amount, not the remainder.'},
       {'kind':'fraction','numerator':1,'denominator':4,'caption':'One quarter is 25 percent of a whole.'}, [
    q('What is 15 percent of 200?','30',['15','185','300'],'15/100 times 200 equals 30.',
      ['Write the percentage as a fraction out of 100.','Multiply 200 by 15/100.','One percent is 2; take fifteen of those parts.'],check={'operation':'fraction','operator':'multiply','left':'200','right':'15/100'}),
    q('What is 40 percent of 60?','24',['20','40','36'],'40/100 simplifies to 2/5. Two fifths of 60 equals 24.',
      ['Find the percentage amount, not the remainder.','Ten percent of 60 is 6.','Take four groups of that ten-percent amount.'],check={'operation':'fraction','operator':'multiply','left':'60','right':'40/100'}),
    q('A 50-unit item has a 20 percent discount. How many units is the discount?', '10',['20','30','40'],'The discount amount is 20/100 times 50, or 10 units. The question does not ask for the final price.',
      ['Identify whether the question asks for discount or final price.','Find 20 percent of 50.','Ten percent is 5, so double that amount.'],check={'operation':'fraction','operator':'multiply','left':'50','right':'20/100'}),
    q('A tank holds 120 litres when full. It currently contains 35 percent of that amount. How many litres are in it?','42',['35','78','85'],'Multiply the full capacity by 35/100: 120 times 0.35 equals 42 litres.',
      ['Use full capacity as the whole amount.','Ten percent is 12 litres and five percent is 6 litres.','Combine three ten-percent parts and one five-percent part.'],check={'operation':'fraction','operator':'multiply','left':'120','right':'35/100'}),
])

lesson('m1215-05','Find and check the mean','maths','12-15','arithmetic_mean',
       'Find an average by sharing a total equally across the values.',
       'The arithmetic mean is the sum of the values divided by how many values there are. Include zero values in the count. A mean need not be one of the original values, and it does not describe every item in the group.',
       {'prompt':'What is the mean of 2, 4 and 9?', 'explanation':'Add to get 15. There are three values, so divide 15 by 3 to get a mean of 5. None of the original values has to equal 5.'},
       {'kind':'counters','groups':[2,4,9],'caption':'These three groups contain fifteen counters in total. Equal sharing would give five per group.'}, [
    q('What is the mean of 4, 6 and 8?','6',['3','8','18'],'The total is 18 and there are three values. 18 divided by 3 equals 6.',
      ['First add all three values.','The total is 18. Count how many values contributed.','Divide the total by 3.'],check={'operation':'mean','values':[4,6,8]}),
    q('What is the mean of 0, 4 and 8?','4',['6','8','12'],'The total is 12. Zero is still one of the three values, so divide by 3 to get 4.',
      ['Zero contributes nothing to the sum but still counts as a value.','There are three values, not two.','Divide their total of 12 by 3.'],check={'operation':'mean','values':[0,4,8]}),
    q('What is the mean of 2, 3, 6 and 7?','4.5',['4','5','6'],'The sum is 18. Dividing by the four values gives 4.5.',
      ['A mean may be between whole numbers.','Add the four values to get 18.','Divide 18 by 4, keeping any fractional part.'],check={'operation':'mean','values':[2,3,6,7]}),
    q('A reader records 10, 0, 20 and 6 minutes on four days. What is the mean number of minutes per day?','9',['12','18','36'],'The four-day total is 36 minutes. Divide by all four days, including the zero-minute day, to get 9.',
      ['Use all four days, including the day with zero minutes.','Add the times to get the total minutes.','Divide the total of 36 by 4 days.'],check={'operation':'mean','values':[10,0,20,6]}),
])

figurative_passage='The workshop woke as the morning group arrived. Tools clinked, stools scraped, and conversation filled the room. Noor called the unfinished model "a puzzle waiting for its last piece." When the final panel fitted, a wave of relief passed through the group. Nobody had moved near water; they were simply glad that the careful adjustments had worked.'
lesson('r1215-04','Read beyond literal meanings','reading','12-15','figurative_language',
       'Interpret figurative language using the surrounding scene.',
       'Figurative language describes something through an imaginative comparison. A room cannot literally wake, but saying it woke can suggest that it became active. Use context to explain the intended meaning without treating the image as a literal event.',
       {'prompt':'What does The workshop woke suggest?', 'explanation':'The following sounds and conversation show activity starting. The writer describes the room as if it were a living thing waking up.'},
       {'kind':'reading','focus':'image → context → intended meaning','caption':'Check the surrounding details before interpreting an image.'}, [
    q('What does The workshop woke convey in this passage?','The room became busy as people arrived.',['The building had been asleep like a person.','The tools repaired themselves.','Everyone left the room.'],'The sounds and conversation support the image of the workshop becoming active.',
      ['Look at the actions after the opening sentence.','Which sounds suggest that activity is beginning?','Choose a meaning about a busy room, not a sleeping building.'],evidence='Tools clinked, stools scraped, and conversation filled the room.'),
    q('Why does Noor call the model a puzzle waiting for its last piece?','One remaining part is needed to complete it.',['The model is definitely a jigsaw puzzle.','All the work must be thrown away.','The model has no parts at all.'],'The unfinished model and final panel support a comparison about completing a whole.',
      ['Connect the comparison to the unfinished model.','What happens when the final panel fits?','Choose the meaning about one last part completing the work.'],evidence='When the final panel fitted'),
    q('What does a wave of relief describe here?','A shared feeling of gladness after the difficulty ends.',['Water flowing across the workshop.','A hand signal to stop working.','A new problem with the panel.'],'The text explicitly explains that nobody was near water and the group was glad the adjustments worked.',
      ['Read the sentence after the wave image.','Is the writer describing water or a feeling?','Choose the feeling connected to the successful adjustments.'],evidence='they were simply glad that the careful adjustments had worked'),
    q('Read: "When the debate ended, the room froze. Nobody moved or spoke for a moment." What does the room froze most likely mean?','The people became suddenly still and silent.',['The temperature fell below freezing.','Ice covered every chair.','The debate lasted through winter.'],'The next sentence explains the stillness and silence; no evidence describes actual ice or temperature.',
      ['Read the sentence that explains the image.','Focus on the people’s movements and speech.','Choose stillness and silence rather than literal freezing.'],evidence='Nobody moved or spoke for a moment.'),
],figurative_passage)

counterexample_passage='A notice claimed, "Every plant in the school garden flowers in spring." The garden club checked its records. The pear tree had flowered in spring, and so had several bulbs. However, a labelled aster in the same garden had flowered only in autumn that year. The club changed the notice to "Some plants in our garden flower in spring." Its report explained that many supporting examples cannot guarantee a claim about every plant, while one clear exception can show that such a claim is too broad.'
lesson('r1215-05','One exception changes a claim','reading','12-15','counterexamples_and_qualifiers',
       'Test words such as every and some against the available evidence.',
       'A claim about every member of a group allows no exceptions. One well-supported exception is enough to challenge it. Some is a more limited claim: it says there are examples, without saying how many or ruling out exceptions.',
       {'prompt':'Do several spring-flowering plants prove that every garden plant flowers in spring?', 'explanation':'No. Those examples support a claim about those plants. A statement about every plant also has to account for plants that were not covered by the examples.'},
       {'kind':'reading','focus':'every → check for an exception','caption':'Match the strength of a claim to the evidence.'}, [
    q('Which record challenges the original claim most directly?','The garden’s aster flowered only in autumn that year.',['The pear tree flowered in spring.','Several bulbs flowered in spring.','The garden club kept records.'],'The aster belongs to the claimed group but does not match the spring-flowering claim.',
      ['The original word every allows no exceptions.','Find a plant in this garden with a different flowering season.','Choose the aster record, which conflicts with the universal claim.'],evidence='a labelled aster in the same garden had flowered only in autumn that year'),
    q('Why do the pear tree and bulb records fail to prove the original claim?','Examples of some plants do not establish a claim about every plant.',['Spring records cannot ever be useful.','The records describe no plants.','One tree represents all possible plants.'],'Supporting examples show what happened for those plants, but they do not rule out an exception elsewhere in the group.',
      ['Compare the plants observed with the word every.','Could another garden plant behave differently?','Choose the explanation that preserves that possibility.'],evidence='many supporting examples cannot guarantee a claim about every plant'),
    q('What does the revised notice assert?','At least some garden plants flower in spring.',['Every garden plant flowers only in spring.','No garden plant flowers in autumn.','Exactly half of the plants flower in spring.'],'Some asserts examples exist without claiming all, an exact fraction, or the absence of autumn flowers.',
      ['Focus on the revised word Some.','Does some specify every plant or an exact number?','Choose the claim that leaves room for other flowering seasons.'],evidence='Some plants in our garden flower in spring.'),
    q('Read: "Kai claimed that every library book has a blue cover. Jo found a library book with a green cover." Assuming the observations are accurate, what follows?','The green-covered library book is an exception to Kai’s claim.',['Every library book must be green.','No library book can be blue.','Kai’s claim is proved by one book.'],'One library book with a non-blue cover contradicts every book being blue. It does not establish the colours of all other books.',
      ['Identify the group and the word every.','Does Jo’s book belong to the group but fail the colour claim?','Reject the universal claim without making a new universal colour claim.'],evidence='Jo found a library book with a green cover.'),
],counterexample_passage)

assert len(lessons) == 30 and question_count == 120
output = Path(__file__).resolve().parents[1] / 'backend/content/lessons.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(lessons, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Wrote {len(lessons)} lessons and {question_count} questions to {output}')
