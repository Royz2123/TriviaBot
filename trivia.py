import time
import os
import re

import util
import questions

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


UNCERTAIN_ANSWER = -1
QUERY_TYPES = 4

THRESH = 40

class TriviaQuestion(object):
    def __init__(self, quest, ans, pre_query=False):
        self._quest = quest
        self._ans = ans
        self._pre_query = pre_query
        
        # Normalize
        self._ans = [opt.lower() for opt in self._ans]
   
        self._responses = [None] * QUERY_TYPES
        
        # create list of all queries
        self._queries = [self._quest]
        self._queries += [''.join([self._quest, ' %s' % choice]) for choice in self._ans]
        
        # pre query if needed
        if self._pre_query:        
            self._responses = [util.get_response(util.google_query(query)) for query in self._queries]
   
    """
    Gets a query from google or loads from cache
    """
    def get_query(self, query_index):
        if self._responses[query_index] is not None:
            return self._responses[query_index]
        self._responses[query_index] = util.get_response(util.google_query(self._queries[query_index]))
        return self._responses[query_index]
        
    """
    Choose answer based on occurences and question format
    """
    def choose_answer(self, ans_occ):
        # TEMP: print occurences
        # print(ans_occ)
    
        # find most probable index
        if ' NOT ' not in self._quest: 
            index = ans_occ.index(max(ans_occ))
        else:
            index = ans_occ.index(min(ans_occ))
        
        # check for uncertainty
        # Method 1 - See if the index shows up more than once.
        # Method 2 - Check for distance from other answers
     
        if ans_occ.count(ans_occ[index]) > 1:
            return UNCERTAIN_ANSWER
            
        # Otherwise return the index of the answer
        return index
     
    """
    Find occurences using fuzzy wuzzy
    """ 
    def count_occurences(self, text, patterns, fuzzy_mode=False):
        if fuzzy_mode:
            # fuzzy count
            occs = dict(
                process.extract(text, patterns, limit=len(patterns))
            )
            occs = [occs[pattern] for pattern in patterns]
            
            # if all are smaller than thresh, useless
            if max(occs) < THRESH:
                return [0] * len(patterns)
            return occs
        else:
            # regular count
            occs = [0] * len(patterns)
            
            # count the occurences of each answer in google
            for i in range(0, len(self._ans)):
                occs[i] += text.count(self._ans[i])
                
            return occs
                
             
    """
    Approach 1: Search for the answer that shows up the most in google
    """
    def method1(self):
        ans_occ = self.count_occurences(self.get_query(0), self._ans)
     
        # return the most probable answer
        return self.choose_answer(ans_occ)


    """
    Approach 2: Search for the answer and the choice together
    """
    def method2(self):  
        total_occ = [0] * len(self._ans)
    
        # query all the choices
        for choice_index in range(1, QUERY_TYPES):
            # count occurences for this query
            curr_occ = self.count_occurences(
                self.get_query(choice_index), 
                self._ans    
            )
            
            # add them to total occurences
            total_occ = [x+y for x,y in zip(total_occ, curr_occ)]

        # return the most probable answer
        return self.choose_answer(total_occ)
        
        
    """
    Approach 3: Similar to approach 1, but award occurences that appeared before
    """
    def method3(self):
        ans_occ = [0] * len(self._ans)
        content = self.get_query(0)
        #print(content)
        
        # count the occurences of each answer in google
        for i in range(0, len(self._ans)):
            occ_indices = [m.start() for m in re.finditer(self._ans[i], content)]
            
            # adjust occurences using reward function
            adjusted_occ = [1 / float(value) for value in occ_indices]
            ans_occ[i] += sum(adjusted_occ)
            
        # return the most probable answer
        return self.choose_answer(ans_occ)
        
    """
    Approach 4: Like approach 1 without fuzziness
    """
    def method4(self):
        ans_occ = self.count_occurences(self.get_query(0), self._ans, False)
     
        # return the most probable answer
        return self.choose_answer(ans_occ)
        
    """
    Approach 5: Like approach 1 with both fuzziness and no fuzziness
    """
    def method5(self):
        occ1 = self.count_occurences(self.get_query(0), self._ans, False)
        occ2 = self.count_occurences(self.get_query(0), self._ans, True)
        print(occ2)
        # add them to total occurences
        total_occ = [x+y for x,y in zip(occ1, occ2)]
     
        # return the most probable answer
        return self.choose_answer(total_occ)
        
        
    ALL_METHODS = [method1, method2, method3]
    CHOSEN_METHODS = [method1, method2, method3, method4, method5]
    
    """
    Strategy1: Basic Poll, Base Strategy
    """
    def strategy1(self, poll_from=0):
        answers = [method(self) for method in TriviaQuestion.CHOSEN_METHODS[poll_from:]]
        print(answers)
        answers = [answer for answer in answers if answer != UNCERTAIN_ANSWER]
        
        # find most likely answer
        try:
            # print("Polled answers: ", list(answers))
            return util.most_common(answers)
        except:
            # All answers were -1, randomly guess its 0
            return 0
        
    """
    Strategy 2: Try answering with the classic method, no answer => max other methods
    """
    def strategy2(self):
        # Try preferred method
        answer_index = self.method1()
        if answer_index != UNCERTAIN_ANSWER:
            return answer_index
    
        # Submit to polling
        # Poll from 1 since we already know method 1 is not worth anything
        return self.strategy1(1)
    
    
    """
    Answer using a certain strategy
    """
    def answer(self):
        print("Question: ", self._quest, "\nOptions: ", self._ans)
    
        # Try answering
        final_index = self.strategy1()
            
        # print answer
        print(self._ans[final_index])
        return final_index
        
      
def ask_question():
    quest = input('Enter Question:')    
    
    options = []
    for i in range(3):
        options.append(input("Next opt (" + str(i+1) + "): "))
        
    # try answering the question - method 1
    question = TriviaQuestion(quest, options)
    question.answer()
    
def demo_questions():
    for question in questions.DEMO_QUESTIONS:
        question = TriviaQuestion(question["question"], question["options"])
        question.answer()
    
def main():
    t_start = time.time()

    demo_questions()
        
    # print total time
    t_end = time.time()
    time_taken = t_end - t_start
    print('Took: %f seconds' % time_taken)

    

if __name__ == "__main__":
    main()

    
    