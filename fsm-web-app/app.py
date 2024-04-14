from fsm import FSM, State
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

finite_state_machines = {}

@app.route('/')
def index():
    return render_template('index.html', fsm_list=finite_state_machines)

@app.route('/create_fsm', methods=['POST'])
def create_fsm():
    fsm_name = request.form.get('fsm_name')
    start_state = request.form.get('start_state')
    if fsm_name not in finite_state_machines:
        print("Creating FSM: " + fsm_name)
        finite_state_machines[fsm_name] = FSM(State(start_state), fsm_name)
    return redirect(url_for('index'))

@app.route('/edit_fsm/<fsm_name>')
def edit_fsm(fsm_name):
    if fsm_name in finite_state_machines:
        fsm = finite_state_machines.get(fsm_name)
        fsm_image = fsm.visualize()
        return render_template('edit_fsm.html', fsm_name=fsm_name, fsm_image=fsm_image)
    else:
        return "FSM not found."

@app.route('/add_transition/<fsm_name>', methods=['POST'])
def add_transition(fsm_name):
    if fsm_name in finite_state_machines:
        fsm = finite_state_machines.get(fsm_name)
        source_state = request.form.get('source_state')
        target_state = request.form.get('target_state')
        probability = float(request.form.get('probability'))
        transition_label = request.form.get('transition-label')
        fsm.add_state(State(source_state))
        fsm.add_state(State(target_state))
        fsm.add_transition(source_state, target_state, transition_label, probability)
        fsm_image = fsm.visualize()

        return render_template('edit_fsm.html', fsm_name=fsm_name, fsm_image=fsm_image)
    else:
        return "FSM not found."

@app.route('/mark_final_state/<fsm_name>', methods=['POST'])
def mark_final_state(fsm_name):
    if fsm_name in finite_state_machines:
        fsm = finite_state_machines.get(fsm_name)
        state_name = request.form.get('state_name')
        fsm.mark_state_as_final(state_name)
        fsm_image = fsm.visualize()

        return render_template('edit_fsm.html', fsm_name=fsm_name, fsm_image=fsm_image)
    else:
        return "FSM not found."


@app.route('/superpose_fsm', methods=['GET'])
def superpose_fsm():
    fsm_name1 = request.args.get('fsm1')
    fsm_name2 = request.args.get('fsm2')

    fsm1 = finite_state_machines.get(fsm_name1)
    fsm2 = finite_state_machines.get(fsm_name2)

    if fsm1 and fsm2:
        superposed_fsm = fsm1.superpose(fsm2)
        print(superposed_fsm.format_as_string())
        finite_state_machines[fsm_name1 + " x " + fsm_name2] = superposed_fsm

        superposed_fsm_image = superposed_fsm.visualize()
        return render_template('superpose_fsm.html', fsm_name1=fsm_name1, fsm_name2=fsm_name2, superposed_fsm_image=superposed_fsm_image)
    else:
        return "One or both FSMs not found."

if __name__ == '__main__':
    app.run(debug=True)
