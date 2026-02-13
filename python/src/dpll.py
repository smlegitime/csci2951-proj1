class DPLL:
    def __init__(self, clauses, symbols):
        self.clauses = clauses
        self.symbols = symbols

    def solve(self, model=None):
        if model is None:
            model = {}
        return self.dpll(self.clauses, self.symbols, model)
    
    def dpll(self, clauses, symbols, model):
        """Main DPLL function"""
        instance_status = self.eval_instance(clauses, model)
        if instance_status =='SAT':
            return model 
        elif instance_status =='UNSAT':
            return None 
        
        # unit propagation
        vars, vals = self.unit_clause(clauses, model)
        if vars is None:
            return None # there's a conflict
        if vars:
            symbols = list(set(symbols) - set(vars))
            model = model | dict(zip(vars, vals))
            return self.dpll(clauses, symbols, model)
        
        # pure literal elimination
        # vars, vals = pure_symbol(clauses, model) 
        # if vars: 
        #     symbols = list(set(symbols) - set(vars))
        #     model = model | dict(zip(vars, vals))
        #     return dpll(clauses, symbols, model)
        
        # branch
        if not symbols:
            return None

        p = self.choose_branching_var(symbols, clauses, model)
        if p is None:
            return None

        rest = [s for s in symbols if s != p]

        res = self.dpll(clauses, rest, (model | {p: True}))
        if res is not None:
            return res
        
        return self.dpll(clauses, rest, (model | {p: False})) # backtracking with False

    def eval_clause(self, clause, model):
        """Evaluates a clause given a model"""
        unassigned = False 
        
        for var in clause:
            if (abs(var) in model):
                value = model[abs(var)]

                if (var > 0 and value) or (var < 0 and not value):
                    return 'TRUE' 
            else: 
                unassigned = True 
        if unassigned:
            return 'UNKNOWN' 
        
        return 'FALSE'

    def eval_instance(self, clauses, model):
        """Evaluates the whole instance"""
        every = True 

        for clause in clauses: 
            clause_value = self.eval_clause(clause, model) 

            if clause_value == 'FALSE': 
                return 'UNSAT' 
            if clause_value != 'TRUE': 
                every = False 
        if every:
            return 'SAT' 
        
        return 'UNKNOWN'

    def unit_clause(self, clauses, model):
        """Unit clause selection and propagation"""
        model = model.copy() 
        new_assignments ={}
        found_unit_clause = True 

        while found_unit_clause: 
            found_unit_clause = False 

            for clause in clauses:
                clause_val = self.eval_clause(clause, model)
                if clause_val == 'TRUE':
                    continue 
                elif clause_val == 'FALSE':
                    return None, None
                
                unassigned = [lit for lit in clause if abs(lit) not in model]

                if len(unassigned) == 1: 
                    literal = unassigned[0]
                    if (abs(literal)) in model: 
                        continue 
                    else: 
                        model[abs(literal)] = literal > 0
                        new_assignments[abs(literal)] = literal > 0
                        found_unit_clause = True

        return list(new_assignments.keys()), list(new_assignments.values())

    def pure_symbol(self, clauses, model):
        """Finds pure literals"""
        pure = {} 
        impure = set()

        for clause in clauses: 
            if self.eval_clause(clause, model) == 'TRUE': 
                continue 

            for x in clause: 
                var = abs(x)

                if var in model or var in impure:
                    continue

                if var not in pure:
                    pure[var] = x > 0

                else: 
                    if pure[var] != (x > 0): 
                        pure.pop(var)
                        impure.add(var)
        if not pure: 
            return [], []
        return list(pure.keys()), list(pure.values())

    def choose_branching_var(self, symbols, clauses, model):
        """Choose next variable for branching based on frequency"""
        var_score = {var: 0 for var in symbols}

        for clause in clauses:
            if self.eval_clause(clause, model) != 'TRUE':
                for lit in clause:
                    var = abs(lit)
                    if var in symbols:
                        var_score[var] += 1

        if not var_score:
            return None
        return max(var_score, key=var_score.get)