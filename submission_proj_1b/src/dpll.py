import random

UNASSIGNED = -1
TRUE = 1
FALSE = 0

class DPLL:
    def __init__(self, clauses):
        self.clauses = clauses
        self.num_vars = max(abs(lit) for clause in clauses for lit in clause)

    def solve(self, model=None):
        if model is None:
            model = [UNASSIGNED] * (self.num_vars + 1)
        return self.dpll(self.clauses, model)
    
    def dpll(self, clauses, model): 
        status = self.eval_instance(clauses, model) 

        if status == TRUE:
            return model 
        if status == FALSE: 
            return None 
        
        assigned_vars = self.unit_clause(clauses, model) 
        if assigned_vars is False: 
            return None 
        
        pure_vars, pure_vals = self.pure_symbol(clauses, model) 
        for var, val in zip(pure_vars, pure_vals): 
            model[var] = val 
        
        var, sign = self.moms(clauses, model)
        if var is None: 
            return model if self.eval_instance(clauses, model) == TRUE else None
        
        new_model = model.copy()
        new_model[var] = TRUE if sign else FALSE 
        result = self.dpll(clauses, new_model)
        if result is not None:
            model[:] = new_model
            return result 
        
        new_model = model.copy() 
        new_model[var] = FALSE if sign else TRUE
        result = self.dpll(clauses, new_model)
        if result is not None:
            model[:] = new_model
            return result
        
        model[var] = UNASSIGNED 
        for v in assigned_vars:
            model[v] = UNASSIGNED
        for v, val in zip(pure_vars, pure_vals): 
            model[v] = UNASSIGNED

        return None 

    def eval_clause(self, clause, model):
        unassigned = False 
        
        for lit in clause: 
            var = abs(lit) 
            val = model[var] 

            if val == UNASSIGNED: 
                unassigned = True 
            else: 
                if (lit > 0 and val == TRUE) or (lit < 0 and val == FALSE):
                    return TRUE 
        
        if unassigned: 
            return UNASSIGNED 
        
        return FALSE 

    def eval_instance(self, clauses, model): 
        all_true = True 
        
        for clause in clauses: 
            clause_value = self.eval_clause(clause, model) 

            if clause_value == FALSE: 
                return FALSE 
            if clause_value != TRUE: 
                all_true = False 
        if all_true:
            return TRUE 
        
        return UNASSIGNED

    def unit_clause(self, clauses, model):
        assigned = []
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                val = self.eval_clause(clause, model)
                if val == FALSE:
                    # conflict
                    for var in assigned:
                        model[var] = UNASSIGNED
                    return False
                if val == TRUE:
                    continue

                unassigned_lits = [lit for lit in clause if model[abs(lit)] == UNASSIGNED]
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    var = abs(lit)
                    model[var] = TRUE if lit > 0 else FALSE
                    assigned.append(var)
                    changed = True
        return assigned


    def pure_symbol(self, clauses, model): 
        num_vars = len(model) - 1
        pure = [0] * (num_vars + 1) 

        for clause in clauses: 
            clause_val = self.eval_clause(clause, model) 
            if clause_val == TRUE: 
                continue 

            for lit in clause: 
                var = abs(lit) 
                if model[var] != UNASSIGNED or pure[var] == 2: 
                    continue 

                if lit > 0: 
                    sign = 1 
                else: 
                    sign = -1 

                if pure[var] == 0: 
                    pure[var] = sign 
                elif pure[var] != sign: 
                    pure[var] = 2 

        vars_list = [] 
        vals_list = [] 
        for var in range(1, num_vars + 1): 
            if pure[var] == 1: 
                vars_list.append(var) 
                vals_list.append(TRUE) 
            elif pure[var] == -1: 
                vars_list.append(var) 
                vals_list.append(FALSE) 
        
        return vars_list, vals_list 
    
    def branch_var(self, clauses, model): 
        num_vars = len(model) - 1
        vars = [0] * (num_vars + 1)
        poss = [0] * (num_vars + 1)
        negs = [0] * (num_vars + 1) 

        for clause in clauses: 
            clause_val = self.eval_clause(clause, model) 
            if clause_val == TRUE: continue 

            for lit in clause: 
                var = abs(lit) 
                if model[var] != UNASSIGNED: continue 

                vars[var] += 1
                if lit > 0: 
                    poss[var] += 1 
                else: 
                    negs[var] += 1 

        candidates = [] 
        for var in range(1, num_vars + 1): 
            if model[var] == UNASSIGNED:
                score = vars[var] 
                if score > 0: 
                    candidates.append((var, score))
        
        if not candidates:
            return None, None

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_k = candidates[:3] 
        best_var = random.choice(top_k)[0]

        sign = poss[best_var] >= negs[best_var]
        return best_var, sign

    def moms(self, clauses, model):
        num_vars=len(model)-1
        min_size=float('inf')
        pos_count = [0] * (num_vars+1)
        neg_count = [0] * (num_vars+1)

        for clause in clauses:
            clause_val = self.eval_clause(clause, model) 
            if clause_val==TRUE:
                continue 
            unassigned=[] 

            for lit in clause: 
                var=abs(lit) 
                if model[var]==UNASSIGNED:
                    unassigned.append(lit) 

            if len(unassigned)==0: 
                continue 
            
            size = len(unassigned) 
            if size < min_size:
                min_size=size 
                pos_count = [0] * (num_vars + 1)
                neg_count = [0] * (num_vars + 1) 

            if size == min_size: 
                for lit in unassigned:
                    var = abs(lit) 
                    if lit > 0: 
                        pos_count[var] += 1
                    else: 
                        neg_count[var] += 1 
            
        best_score = -1
        best_vars = [] 

        for var in range(1, num_vars+1): 
            if model[var] != UNASSIGNED:
                continue 

            score = pos_count[var] + neg_count[var] 

            if score > best_score: 
                best_score = score 
                best_vars = [var] 
            elif score == best_score and score > 0: 
                best_vars.append(var) 

        if not best_vars: 
            return None, None 

        best_var = random.choice(best_vars) 
        sign = pos_count[best_var] > neg_count[best_var]
        return best_var, sign