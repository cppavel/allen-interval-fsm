import random
import math
from typing import List
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from io import BytesIO
import base64


class State:
    def __init__(self, label):
        self.label = label
        self.transitions = {}
        self.probabilities = {}
    
    def add_transition(self, other, symbol, probability):
        self.transitions[symbol] = other
        self.probabilities[symbol] = probability


class FSM:
    def __init__(self, start, name):
        self.start = start
        self.name = name
        self.states = {}
        self.final_states = set()
        self.states[self.start.label] = self.start
        self.alphabet = set()
        self.image = nx.DiGraph()

    def add_state(self, state):
        if not state.label in self.states:
            self.states[state.label] = state

    def mark_state_as_final(self, state_label):
        if not state_label in self.states:
            return 

        self.final_states.add(state_label)
    
    def add_transition(self, prev_state_label, next_state_label, symbol: str, probability):
        self.alphabet.add(symbol)
        self.image.add_edge(prev_state_label, next_state_label)
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

    def get_edge_labels(self):
        result = {}
        for state_label in self.states:
            for symbol, next_state in self.states[state_label].transitions.items():
                probability = self.states[state_label].probabilities[symbol]
                result[(state_label, next_state.label)] = f"{symbol}, {probability:.2f}"

        return result

    def visualize_fsm(self):
        pos = graphviz_layout(self.image)
        plt.figure()
        node_colors = []
        for node in self.image.nodes:
            if node == self.start.label:
                node_colors.append('green')
            elif node in self.final_states:
                node_colors.append('red')
            else:
                node_colors.append('skyblue')
      
        nx.draw(self.image, pos, with_labels=True, node_size=400, node_color=node_colors, font_size=8, font_color='black', font_weight='bold', arrowsize=12)
        edge_labels = self.get_edge_labels()
        print(edge_labels)
        nx.draw_networkx_edge_labels(
            self.image, pos,
            edge_labels=edge_labels,
            font_color='red'
        )
        
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    def superpose(self, other, is_clock = False):
        start_state = (State(self.start.label + "," + other.start.label), self.start.label, other.start.label)

        super_fsm = FSM(start_state[0], self.name + " x " + other.name)

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