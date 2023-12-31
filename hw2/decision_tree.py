import argparse
from math import log

# DEBUG = True
DEBUG = False

### 1. Implementing the tree data structure
class Node:
    def __init__(self, name=None, j=None, c=None, left=None, right=None):
        self.left = left
        self.right = right
        self.name = name
        self.j = j
        self.c = c

    ### 3. The logic of classifying a new data point
    def classify(self, data_point):
        if not self.name == None: # we have arrived at a node with a class label
            return self.name
        elif data_point[self.j] >= self.c:
            return self.left.classify(data_point)
        else:
            return self.right.classify(data_point)
    ### 3 end

    def count_nodes(self):
        result = 1
        if not self.left == None:
            result += self.left.count_nodes()
        if not self.right == None:
            result += self.right.count_nodes()
        return result

    def PrintTree(self, r=0):
        # we first define how many preceding spaces to print for pretty formatting
        num_features = 2
        cond_str = f'x[{num_features}] >= '
        spacing = len(cond_str)
        if r > 0:
            spacing += r*(spacing+3)

        # we then print relevant information about a node
        if not self.name == None:
            print(self.name, end="")
        if not self.j == None:
            print(f'x[{self.j}] >= {self.c}', end="")
        print()

        # lastly, we recurse into each of its children
        if self.left:
            print(' '*(spacing), end="")
            print('l: ', end="")
            self.left.PrintTree(r+1)
        if self.right:
            print(' '*(spacing), end="")
            print('r: ', end="")
            self.right.PrintTree(r+1)
### 1 end

### 2. The logic of building the tree. The entropy calculations and the split logic
def H_D(Y): # entropy of Y
    classes = [0,1]
    size = len(Y)
    counts = [sum(1 for i in Y if i[2] == cls) for cls in classes]
    P_Y = [count/size for count in counts]
    H_y = - sum(p * log(p, 2) if p > 0 else 0 for p in P_Y)
    return H_y

def determine_candidate_splits(D, features_used): # where D is the set of training instances in this subtree
    fu = {f for f in features_used}
    # S = FindBestSplit(D, C)
    num_features = 2
    candidate_splits = []
    if len(D) == 1: # If we only have one data point, don't even bother
        return candidate_splits

    for j in range(num_features):
        if j in fu:
            if DEBUG:
                print(f'skipping feature {j} because it is in features_used')
            continue # we skip features upon which we have already split
        
        run_j = sorted(D, key= lambda x: x[j])
        # print(run_j)
        entropy_before_split = H_D(run_j)
        if DEBUG:   
            # print(f'ordered by x_{j}, entropy_before_split={entropy_before_split}')
            pass
        
        # c_prev = run_j[0][j]
        c_prev = None
        for c_idx in range(0,len(D)):
            c = run_j[c_idx][j]

            # Before we calculate things, make sure this split would actually split the array
            # for example, with 3 entries of 0.0, the second entry should not be treated as a valid
            # split threshold, as it doesn't actually separate entries
            # since our split is x[j] >= c, 
            if c == c_prev:
                continue    # do not consider a split threshold we've already seen
            else:
                c_prev = c # we only consider this threshold if we haven't just seen it

            # Begin doing all calculations
            a = run_j[0:c_idx]
            frac_a = len(a) / len(run_j)
            b = run_j[c_idx:]
            frac_b = len(b) / len(run_j)

            # entropy_split = - sum of { p(Child) * log_2(Child)}
            # where p(Child) is the probability of an observation being in a given child
            # i.e. the number of observations in a child / total observations
            # i.e. frac_a, frac_b
            # TOOD check for extremes
            if frac_a == 0 or frac_b == 0:
                entropy_split = 0
            else:
                entropy_split = - (frac_a*log(2, frac_a) + frac_b*log(2, frac_b))

            ### 2.3
            if DEBUG:
                print(f'For cut X[{j}] >= {c}, ', end='')

            # check if 0, if so stop
            if entropy_split == 0:
                if DEBUG:
                    print(f'Split Entropy = 0, mutual information={entropy_before_split}')
                continue

            H_D_cond_a = H_D(a)
            H_D_cond_b = H_D(b)
            H_y_c = (frac_a * H_D_cond_a) + (frac_b * H_D_cond_b)
            info_gain = entropy_before_split - H_y_c
            gain_ratio = info_gain / entropy_split

            # print(f'for splits a={a} frac_a={frac_a}, b={b} frac_b{frac_b}, we have')
            # print(f'H_D_cond_a = {H_D_cond_a}, H_D_cond_b = {H_D_cond_b}')
            # print(f'Combined, {frac_a}*{H_D_cond_a} + {frac_b}*{H_D_cond_b} = {H_y_c}')
            # check if 0, if so stop

            if DEBUG:
                print(f'Gain Ratio = {gain_ratio}')
            if gain_ratio == 0:
                continue
                # return None
            candidate_split = (j,c, entropy_split, gain_ratio)
            # print(candidate_split)
            candidate_splits.append((j,c, entropy_split, gain_ratio))
    
    return candidate_splits

def find_best_split(C): # where D is the set of training instances in this subtree, C is the candidate splits
    gain_ratio_max_val = 0
    gain_ratio_max_params = None
    for j, c, entropy_split, gain_ratio in C:
        if gain_ratio > gain_ratio_max_val:
            gain_ratio_max_val = gain_ratio
            gain_ratio_max_params = (j, c)
    return gain_ratio_max_params

def make_subtree(D, features_used={}): # where D is the set of training instances
    if DEBUG:
        print('\n>>> Entering recursive call')
    fu = {f for f in features_used}
    N = Node()
    C = determine_candidate_splits(D, fu)
    if DEBUG:
        # print(f'Input Data={D}')
        # print(f'Candidate Splits={sorted(C, key= lambda x: x[3])}')
        pass
    if len(C) == 0: # stopping criteria have been met
        # find majority class in D, make it N's class label. If not majority, predict y=1
        if DEBUG:
            print(f'Making leaf node, counting 1s and 0s in {D}')
        count_1 = sum(1 for i in D if i[2] == 1)
        count_0 = len(D) - count_1
        if DEBUG:
            print(f'count_1={count_1}, count_0={count_0}')
        N.name = 1 if count_1 >= count_0 else 0 
        if DEBUG:
            print(f'Stopping Condition met, Node.name={N.name}')
    else:
        best_split = find_best_split(C)
        j, c = best_split
        fu.add(j) # make sure to add the feature we split on to the set of features used
        if DEBUG:
            print(f'best_split=({j},{c})')
        left = []
        right = []
        for entry in D:
            if entry[j] >= c:
                left.append(entry)
            else:
                right.append(entry)
        N = Node(j=j, c=c)
        if(DEBUG):
            print(f'Found worthy split, left={left}, right={right}')
            pass
        N.left = make_subtree(left, fu)
        N.right = make_subtree(right, fu)
    if DEBUG:
        print(f'N about to be returned=(name={N.name}, j={N.j}, c={N.c})')
    return N
### 2 end

def get_observations(filepath):
    observations = []
    f = open(filepath)
    for line in f.readlines():
        # print(line.strip())
        observation = tuple(float(e) for e in line.strip().split(sep=" "))
        observations.append(observation)
    return observations

if __name__ == "__main__":
    # This allows the user to pass a file path in and have its tree generated
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath')
    args = parser.parse_args()
    filepath = args.filepath
    observations = get_observations(filepath)

    if DEBUG:
            print("<<< We start making the decision tree >>>")
    root = make_subtree(observations)
    root.PrintTree()

    ### We ask user for new points to classify
    while(True):
        print("Please provide a new point to classify (should have form `x0 x1` similar to input files)")
        new_point = tuple(float(e) for e in input().strip().split(sep=" "))
        point_class = root.classify(new_point)
        print(f'The predicted class for this point is {point_class}\n')