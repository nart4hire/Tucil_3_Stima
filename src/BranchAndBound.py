import os
import sys
import random
import time
import threading
import signal
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style
from copy import deepcopy

# Global Constants
VERBOSE = False
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
DEPTH = None

if len(sys.argv) > 2:
    if sys.argv[1] == "-verbose" or sys.argv[1] == "-v":
        VERBOSE = True
    if sys.argv[2].isnumeric():
        DEPTH = int(sys.argv[2])
        NEW_PATH = None
    else:
        NEW_PATH = CUR_PATH[:-3] + "test\\" + sys.argv[2]
        if not os.path.exists(NEW_PATH):
            print("File Doesn't Exist, Running Default Script")
            NEW_PATH = None
elif len(sys.argv) > 1:
    if sys.argv[1] == "-verbose" or sys.argv[1] == "-v":
        VERBOSE = True
        NEW_PATH = None
    elif sys.argv[1].isnumeric():
        DEPTH = int(sys.argv[1])
        NEW_PATH = None
    else:
        NEW_PATH = CUR_PATH[:-3] + "test\\" + sys.argv[1]
        if not os.path.exists(NEW_PATH):
            print("File Doesn't Exist, Running Default Script")
            NEW_PATH = None

ENDSTATE = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]

# unicode for terminal drawing
BOTTOM_LEFT = '\u2514'
BOTTOM_RIGHT = '\u2518'
TOP_LEFT = '\u250C'
TOP_RIGHT = '\u2510'

CROSSROAD = '\u253C'
TOP_T_JUNCTION = '\u252C'
BOTTOM_T_JUNCTION = '\u2534'
LEFT_T_JUNCTION = '\u251C'
RIGHT_T_JUNCTION = '\u2524'
VERTICAL = Style.BRIGHT + Fore.BLUE + '\u2502' + Fore.RESET + Style.RESET_ALL
HORIZONTAL = '\u2500'

# Separator Line Constants
TOP_LINE = Style.BRIGHT + Fore.BLUE + TOP_LEFT + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + TOP_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + TOP_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + TOP_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + TOP_RIGHT + Fore.RESET + Style.RESET_ALL
MIDDLE_LINE = Style.BRIGHT + Fore.BLUE + LEFT_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + CROSSROAD + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + CROSSROAD + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + CROSSROAD + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + RIGHT_T_JUNCTION + Fore.RESET + Style.RESET_ALL
BOTTOM_LINE = Style.BRIGHT + Fore.BLUE + BOTTOM_LEFT + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + BOTTOM_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + BOTTOM_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + BOTTOM_T_JUNCTION + HORIZONTAL + HORIZONTAL + HORIZONTAL + HORIZONTAL + BOTTOM_RIGHT + Fore.RESET + Style.RESET_ALL

# Output Constants
LEFT_BRACKET = Style.BRIGHT + Fore.BLUE + HORIZONTAL + HORIZONTAL + RIGHT_T_JUNCTION + Fore.RESET + Style.RESET_ALL
RIGHT_BRACKET = Style.BRIGHT + Fore.BLUE + LEFT_T_JUNCTION + HORIZONTAL + HORIZONTAL + Fore.RESET + Style.RESET_ALL

class Node:
    def __init__(self, _position, _parent = None, _direction = None, _bounded = False, _solution = False):
        self.position = _position
        self.parent = _parent
        if self.parent != None:
            self.cost = self.f() + self.g(ENDSTATE)
        else:
            self.cost = None
        self.direction = _direction
        self.bounded = _bounded
        self.solution = _solution
        self.child = list()

    def f(self):
        if self.parent == None:
            return 0
        else:
            return 1 + self.parent.f()

    def g(self, endpos):
        endpos_flat = [item for array in endpos for item in array]
        curpos_flat = [item for array in self.position for item in array]
        count = 0
        for i, num in enumerate(curpos_flat):
            if num != 0 and i != endpos_flat.index(num):
                count += 1
        return count

    def addChild(self, _child):
        self.child.append(_child)

    def getParent(self):
        return self.parent

    def getChildren(self):
        return self.child

    def getPosition(self):
        return self.position

    def getDirection(self):
        return self.direction

    def getCost(self):
        return self.cost

    def isBounded(self):
        return self.bounded

    def toggleBounded(self):
        self.bounded = not self.bounded

    def toggleSolution(self):
        self.solution = not self.solution

    def __repr__(self, indent=0):
        space = " "
        first  = "| " + str(self.position[0][0]).rjust(2) + " " + str(self.position[0][1]).rjust(2) + " " + str(self.position[0][2]).rjust(2) + " " + str(self.position[0][3]).rjust(2) + " | " + str(self.direction) + ",\n"
        second = "| " + str(self.position[1][0]).rjust(2) + " " + str(self.position[1][1]).rjust(2) + " " + str(self.position[1][2]).rjust(2) + " " + str(self.position[1][3]).rjust(2) + " | " + str(self.cost) + ",\n"
        third  = "| " + str(self.position[2][0]).rjust(2) + " " + str(self.position[2][1]).rjust(2) + " " + str(self.position[2][2]).rjust(2) + " " + str(self.position[2][3]).rjust(2) + " | " + ("Bounded" if self.bounded else "UnBounded") + ",\n"
        fourth = "| " + str(self.position[3][0]).rjust(2) + " " + str(self.position[3][1]).rjust(2) + " " + str(self.position[3][2]).rjust(2) + " " + str(self.position[3][3]).rjust(2) + " | " + ("Solution" if self.solution else "Not Solution")
        return space * indent + first + space * indent + second + space * indent + third + space * indent + fourth

# 15-Puzzle Print
def displayPuzzle(node: Node):
    matrix = node.position
    print(TOP_LINE)
    for i, array in enumerate(matrix):
        for j, num in enumerate(array):
            print(VERTICAL, end=' ')
            if ENDSTATE[i][j] == num:
                print(Style.BRIGHT + Fore.GREEN, end='')
            else:
                print(Style.BRIGHT + Fore.RED, end='')
            if num == 0:
                print(Fore.RESET + Style.RESET_ALL, end='   ')
            elif num < 10:
                print(str(num) + Fore.RESET + Style.RESET_ALL, end='  ')
            else:
                print(str(num) + Fore.RESET + Style.RESET_ALL, end=' ')
        print(VERTICAL)
        if matrix.index(array) == 3:
            print(BOTTOM_LINE)
        else:
            print(MIDDLE_LINE)

# PseudoRandom Scramble
def getScramble():
    scramble = list()
    matrix = deepcopy(ENDSTATE)

    if DEPTH == None:
        depth = random.randint(12, 18)
    else:
        depth = DEPTH

    for i, array in enumerate(matrix):
        if 0 in array:
            j = array.index(0)
            idx_i = i
            idx_i_copy = i
            idx_j = j
            idx_j_copy = j

    while len(scramble) < depth:
        rdm = None
        while True:
            rdm = random.randint(0, 3)
            if len(scramble) > 0 and scramble[-1] == (2 + rdm) % 4:
                continue
            match rdm:
                case 0 if idx_i_copy < 3:
                    idx_i_copy += 1
                    break
                case 1 if idx_j_copy > 0:
                    idx_j_copy -= 1
                    break
                case 2 if idx_i_copy > 0:
                    idx_i_copy -= 1
                    break
                case 3 if idx_j_copy < 3:
                    idx_j_copy += 1
                    break
        scramble.append(rdm)

    for dir in scramble:
        match dir:
            case 0:
                matrix[idx_i][idx_j], matrix[idx_i + 1][idx_j] = matrix[idx_i + 1][idx_j], matrix[idx_i][idx_j]
                idx_i += 1
            case 1:
                matrix[idx_i][idx_j], matrix[idx_i][idx_j - 1] = matrix[idx_i][idx_j - 1], matrix[idx_i][idx_j]
                idx_j -= 1
            case 2:
                matrix[idx_i][idx_j], matrix[idx_i - 1][idx_j] = matrix[idx_i - 1][idx_j], matrix[idx_i][idx_j]
                idx_i -= 1
            case 3:
                matrix[idx_i][idx_j], matrix[idx_i][idx_j + 1] = matrix[idx_i][idx_j + 1], matrix[idx_i][idx_j]
                idx_j += 1

    return matrix

def Reachable(endpos, curpos):
    endpos_flat = [item for array in endpos for item in array]
    curpos_flat = [item for array in curpos for item in array]
    count = 0

    d = dict()
    for i in range(1, 16):
        d[str(i)] = 0
    d['0'] = 0
    d['X'] = 0

    for i, num in enumerate(curpos_flat):
        kurang = 0
        idx_i = endpos_flat.index(num)
        for j in range(i + 1, len(curpos_flat)):
            idx_j = endpos_flat.index(curpos_flat[j])
            if idx_j < idx_i:
                kurang += 1
        d[str(num)] = kurang
        count += kurang

    if curpos_flat.index(0) in [1, 3, 4, 6, 9, 11, 12, 14]:
        d['X'] = 1
        count += 1

    d['Total'] = count
    df = pd.DataFrame(d, index=[0])
    print(tabulate(df.T))
    print("The Value Of Reachability is:", count)

    if count % 2 == 0:
        print("Hence the End State is Reachable")
        return True
    else:
        print("Hence the End State is Unreachable")
        return False

def getMoves(node: Node):
    matrix = node.getPosition()
    prevdir = node.getDirection()

    match prevdir:
        case "UP":
            prevmove = 0
        case "RIGHT":
            prevmove = 1
        case "DOWN":
            prevmove = 2
        case "LEFT":
            prevmove = 3
        case _:
            prevmove = -1

    for i, array in enumerate(matrix):
        if 0 in array:
            j = array.index(0)
            # Move Up
            if i < 3 and prevmove != 2:
                u = deepcopy(matrix)
                u[i][j], u[i + 1][j] = u[i + 1][j], u[i][j]
            else:
                u = None
            # Move Right
            if j > 0 and prevmove != 3:
                r = deepcopy(matrix)
                r[i][j], r[i][j - 1] = r[i][j - 1], r[i][j]
            else:
                r = None
            # Move Down
            if i > 0 and prevmove != 0:
                d = deepcopy(matrix)
                d[i][j], d[i - 1][j] = d[i - 1][j], d[i][j]
            else:
                d = None
            # Move Left
            if j < 3 and prevmove != 1:
                l = deepcopy(matrix)
                l[i][j], l[i][j + 1] = l[i][j + 1], l[i][j]
            else:
                l = None

    return [u, r, d, l]

def loading():
    for c in ['   ', '.  ', '.. ', '...']:
        sys.stdout.write('Calculating Best Route' + c + '\r')
        sys.stdout.flush()
        time.sleep(0.1)

class BranchAndBound:
    def __init__(self, _position):
        self.root = Node(_position)
        self.queue = list()
        self.solutions = list()
        self.paths = list()
        self.handler = threading.Event()
        self.nodecount = 0
        self.starttime = 0
        self.endtime = 0
        if Reachable(ENDSTATE, self.root.position):
            self.queue.append(self.root)
            self.nodecount += 1
            signal.signal(signal.SIGINT, self.signal_handler)
            process = threading.Thread(target=self.solve)
            if VERBOSE:
                process.daemon = True
                print("\nOrder of Node Expansion:")
                process.start()
                while process.is_alive():
                    time.sleep(1)
            else:
                process.start()
                while process.is_alive():
                    loading()
                sys.stdout.write('                         ')

            if self.handler.is_set():
                sys.exit("\nProcess Interupted, Exiting...")

            for i, path in enumerate(self.paths):
                if len(self.paths) == 1:
                    print("\nSingle Best Solution:")
                else:
                    print("\nBest Solution " + str(i + 1) + ":\n")
                if VERBOSE:
                    print("--- Initial State ---")
                    print(tabulate(self.root.position, tablefmt="grid"))
                else:
                    print(LEFT_BRACKET + "INITIAL STATE" + RIGHT_BRACKET)
                    displayPuzzle(self.root)
                for node in path:
                    if VERBOSE:
                        print("--- " + node.direction + " ---")
                        print(tabulate(node.position, tablefmt="grid"))
                    else:
                        print(LEFT_BRACKET + node.direction + RIGHT_BRACKET)
                        displayPuzzle(node)

            if VERBOSE:
                print("\n--- Total Nodes: " + str(self.nodecount) + " ---")
                print("\n--- Time Taken : {:.3f}ms ---".format((self.endtime - self.starttime) * 1000))
            else:
                print("\n" + LEFT_BRACKET + "Total Nodes: " + str(self.nodecount) + RIGHT_BRACKET)
                print("\n" + LEFT_BRACKET + "Time Taken : {:.3f}ms".format((self.endtime - self.starttime) * 1000) + RIGHT_BRACKET)

        else:
            print("\nEnd State Unreachable, Exiting...")
            sys.exit()

    def raiseNodes(self, root_node: Node):
        posarr = getMoves(root_node)
        for i, pos in enumerate(posarr):
            if pos != None:
                match i:
                    case 0:
                        child = Node(pos, root_node, 'UP')
                    case 1:
                        child = Node(pos, root_node, 'RIGHT')
                    case 2:
                        child = Node(pos, root_node, 'DOWN')
                    case 3:
                        child = Node(pos, root_node, 'LEFT')
                if VERBOSE:
                    print(tabulate(child.position, tablefmt="grid"))
                root_node.addChild(child)
                self.queue.append(child)
                self.nodecount += 1
                for solution in self.solutions:
                    if solution.getCost() < child.getCost() and child in self.queue:
                        child.toggleBounded()
                        self.queue.remove(child)
        self.queue.remove(root_node)

    def findLowestCost(self):
        best = None
        for node in self.queue:
            if not node.isBounded():
                if best == None:
                    best = node
                elif best.getCost() > node.getCost():
                    best = node
        return best

    def getSolved(self):
        solution = None
        for node in self.queue:
            if node.position == ENDSTATE:
                solution = node
                solution.toggleSolution()
            if solution != None and solution not in self.solutions:
                for node in self.queue:
                    if node.getCost() > solution.getCost() and not node.isBounded():
                        node.toggleBounded()
                        self.queue.remove(node)
                self.solutions.append(solution)
                self.queue.remove(solution)

    def solve(self):
        self.starttime = time.time()

        while not self.handler.is_set():
            self.getSolved()
            next = self.findLowestCost()
            if next == None:
                break
            else:
                self.raiseNodes(next)

        self.endtime = time.time()

        mincost = None
        for solution in self.solutions:
            if mincost == None:
                mincost = solution.getCost()
            elif mincost > solution.getCost():
                mincost = solution.getCost()

        for solution in self.solutions:
            if solution.getCost() > mincost:
                solution.toggleSolution()
                solution.toggleBounded()
                self.solutions.remove(solution)

        for solution in self.solutions:
            path = list()
            node = solution
            while node.getParent() != None:
                path.append(node)
                node = node.getParent()
            path.reverse()
            self.paths.append(path)

    def signal_handler(self, signum, frame):
        self.handler.set()

    def printTree(self, node: Node = None, spaces = 0):
        if node == None:
            print("\nState Space Tree:\n")
            print('+')
            print(self.root)
            self.printTree(self.root, 2)
        else:
            for child in node.getChildren():
                print(' ' * spaces + '+')
                print(child.__repr__(spaces))
                self.printTree(child, spaces + 2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and NEW_PATH != None:
        with open(NEW_PATH, 'r') as f:
            lines = f.readlines()
            array = [[int(num) for num in line.split()] for line in lines]
    else:
        array = getScramble()

    if VERBOSE:
        print("--- INPUT ---")
        print(tabulate(array, tablefmt="grid"))
    else:
        print(LEFT_BRACKET + "INPUT" + RIGHT_BRACKET)
        displayPuzzle(Node(array))

    bnb = BranchAndBound(array)

    if VERBOSE:
        bnb.printTree()
        print("\nSolutions:")
        for i, path in enumerate(bnb.paths):
            print("Solution no." + str(i + 1))
            for node in path:
                print(node)
            print("This Solution Has " + str(len(path)) + " Moves")