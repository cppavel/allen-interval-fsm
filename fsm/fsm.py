import random
import math

from automata.fa.nfa import NFA
from allen import compute_allen_count
from typing import List
from combinatorics import calculate_long_relation_count_superposed

def get_clock_fsm(count):

    if count < 2:
        raise Exception("Too few states for clock")

    start_clock = State("0")
    clock_fsm = FSM(start_clock)
    clock_fsm.add_state(State(str(count - 1)))
    clock_fsm.mark_state_as_final(str(count - 1))

    for i in range(1, count, 1):
        clock_fsm.add_state(State(str(i)))
        clock_fsm.add_transition(str(i - 1), str(i), "t", 1.0)

    return clock_fsm

class State:
    def __init__(self, label):
        self.label = label
        self.transitions = {}
        self.probabilities = {}
    
    def add_transition(self, other, symbol, probability):
        self.transitions[symbol] = other
        self.probabilities[symbol] = probability


class FSM:
    def __init__(self, start):
        self.start = start
        self.states = {}
        self.final_states = set()
        self.states[self.start.label] = self.start
        self.alphabet = set()

    def add_state(self, state):
        self.states[state.label] = state

    def mark_state_as_final(self, state_label):
        self.final_states.add(state_label)
    
    def add_transition(self, prev_state_label, next_state_label, symbol: str, probability):
        self.alphabet.add(symbol)
        self.states[prev_state_label].add_transition(self.states[next_state_label], symbol, probability)

    def find_all_paths_to_final_state(self):
        ans = []
        self._find_all_paths_to_final_state_helper(ans, [], self.start)
        return ans

    def _find_all_paths_to_final_state_helper(self, paths: List[List[str]], current_path: List[str], current_state: State):
        if current_state.label in self.final_states:
            paths.append(current_path.copy())

        for symbol, next_state in current_state.transitions.items():
            current_path.append(symbol)
            self._find_all_paths_to_final_state_helper(paths, current_path, self.states[next_state.label])
            current_path.pop(-1)



    def superpose(self, other, is_clock = False):
        start_state = (State(self.start.label + "," + other.start.label), self.start.label, other.start.label)

        super_fsm = FSM(start_state[0])

        state_queue = []
        state_queue.append(start_state)

        while len(state_queue) > 0:
            current_state = state_queue.pop(0)

            fsm1_cur_state_label = current_state[1]
            fsm2_cur_state_label = current_state[2]
            super_fsm_label = current_state[0].label

            if not is_clock:
                for symbol, next_state in self.states[fsm1_cur_state_label].transitions.items():
                    new_state = State(next_state.label+","+fsm2_cur_state_label)
                    super_fsm.add_state(new_state)
        
                    if next_state.label in self.final_states and fsm2_cur_state_label in other.final_states:
                        super_fsm.mark_state_as_final(new_state.label)

                    probability_fsm1 = self.states[fsm1_cur_state_label].probabilities[symbol]
                    probability_fsm2 = 1 - sum(
                        [x[1] for x in other.states[fsm2_cur_state_label].probabilities.items()])
                    probability = probability_fsm1 * probability_fsm2

                    super_fsm.add_transition(
                        super_fsm_label, new_state.label, symbol, probability)
                    state_queue.append((new_state, next_state.label, fsm2_cur_state_label))

            for symbol, next_state in other.states[fsm2_cur_state_label].transitions.items():
                new_state = State(fsm1_cur_state_label+","+next_state.label)
                super_fsm.add_state(new_state)
                if (is_clock and fsm1_cur_state_label in self.final_states):
                    super_fsm.mark_state_as_final(new_state.label)
                elif next_state.label in other.final_states and fsm1_cur_state_label in self.final_states:
                    super_fsm.mark_state_as_final(new_state.label)

                probability_fsm1 = 1 - sum(
                    [x[1] for x in self.states[fsm1_cur_state_label].probabilities.items()])
                probability_fsm2 = other.states[fsm2_cur_state_label].probabilities[symbol]
                probability = probability_fsm1 * probability_fsm2

                super_fsm.add_transition(super_fsm_label, new_state.label, symbol, probability)
                state_queue.append((new_state, fsm1_cur_state_label, next_state.label))


            for symbol_1, next_state_1 in self.states[fsm1_cur_state_label].transitions.items():
                for symbol_2, next_state_2 in other.states[fsm2_cur_state_label].transitions.items():
                    new_state = State(next_state_1.label+","+next_state_2.label)
                    super_fsm.add_state(new_state)
                    if is_clock and next_state_1.label in self.final_states:
                        super_fsm.mark_state_as_final(new_state.label)
                    elif next_state_1.label in self.final_states and next_state_2.label in other.final_states:
                        super_fsm.mark_state_as_final(new_state.label)

                    probability_fsm1 = self.states[fsm1_cur_state_label].probabilities[symbol_1]
                    probability_fsm2 = other.states[fsm2_cur_state_label].probabilities[symbol_2]
                    probability = probability_fsm1 * probability_fsm2

                    super_fsm.add_transition(
                        super_fsm_label, new_state.label, symbol_1 + "," + symbol_2, probability)
                    state_queue.append((new_state, next_state_1.label, next_state_2.label))

        return super_fsm


    def format_as_string(self)->str:
        string = f"State labels: {self.states.keys()}"

        for state_label, state in self.states.items():
            string += f"\n{state_label}:{[state_label + '->' + x[0] + '->' + x[1].label for x in state.transitions.items()]}"

        return string

    def visualize(self, add_prob = False) -> NFA:
        states = set(self.states.keys())

        transitions = {}
        input_symbols = set()
        for state_label, state in self.states.items():
            transitions[state_label] = {}
            
            for symbol, next_state in state.transitions.items():
                probability = state.probabilities[symbol]
                symbol_eff = (symbol 
                        if not add_prob else symbol + f"_{probability}")
                input_symbols.add(symbol_eff)
                transitions[state_label][symbol_eff] = set()
                transitions[state_label][symbol_eff].add(next_state.label)

        initial_state = self.start.label
        final_states = self.final_states

        visual_dfa = NFA(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
        )

        return visual_dfa

    def simulate(self):
        current_state = self.states[self.start.label]
        path = []
        invalid = False
        while current_state.label not in self.final_states:

            if len(current_state.transitions) <= 0:
                invalid = True
                break

            random_number = random.random()
            sum_of_prob = sum([x[1] for x in current_state.probabilities.items()])

            current_sum_of_prob = 0.0
            i = 0

            probabilities = list(current_state.probabilities.items())

            while current_sum_of_prob / sum_of_prob < random_number:
                current_sum_of_prob += probabilities[i][1]
                i+=1

            decision = probabilities[i-1][0]
            next_state_label = current_state.transitions[decision].label
            current_state = self.states[next_state_label]
            path.append(decision)

        return (path, invalid)


def monte_carlo(clocked_intervals_fsm, trials = 100000):
    trial_count = 0 

    paths = []
    while trial_count < trials:
        path, invalid = clocked_intervals_fsm.simulate()

        if not invalid:
            paths.append(path)
        
        trial_count+=1

    allen_count = compute_allen_count(paths)
    total_count = sum([x for x in allen_count.values()])

    print(f"Total count: {total_count}")
    print(f"Count of each relation: {allen_count}")


if __name__ == "__main__":
    start_1 = State("u_a")
    fsm_1 = FSM(start_1)
    fsm_1.add_state(State("li_a"))
    fsm_1.add_state(State("d_a"))
    fsm_1.mark_state_as_final("d_a")
    fsm_1.add_transition("u_a", "li_a", "la", 0.5)
    fsm_1.add_transition("li_a", "d_a", "ra", 0.5)

    start_2 = State("u_b")
    fsm_2 = FSM(start_2)
    fsm_2.add_state(State("li_b"))
    fsm_2.add_state(State("d_b"))
    fsm_2.mark_state_as_final("d_b")
    fsm_2.add_transition("u_b", "li_b", "lb", 0.5)
    fsm_2.add_transition("li_b", "d_b", "rb", 0.5)

    superpose_fsm = fsm_1.superpose(fsm_2)
    clock_fsm = get_clock_fsm(25)
    clocked_fsm = superpose_fsm.superpose(clock_fsm, is_clock=True)
    monte_carlo(clocked_fsm, 500000)
