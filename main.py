import numpy as np

import object_loader
import processor
import inner_line_harvester
import hallway_maker
import indoor_graph
import visualizer

"""##### GLOBAL FIELD #####"""
# for the drawing
MAGNIFICATION = 50

# for the calculation
INNER_WALL_THICKNESS = 0.2
OUTER_WALL_THICKNESS = 0.5
MIN_HALL_WIDTH = 1.2

if __name__ == '__main__':
    """##### (1) 도면파일의 데이터 추출 단계 #####"""
    wall_line_list = []
    door_line_list = []
    arc_list = []
    door_block_list = []
    door_list = []
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0

    # csv file load
    csv_data = np.genfromtxt('drawings/8F_wall_trim_no_EV.csv', delimiter=',', dtype=None, encoding='UTF-8')
    # csv_data = np.genfromtxt('drawings/4F_no_EV.csv', delimiter=',', dtype=None, encoding='UTF-8') # -> 닫힌공간 실패, island 문제
    # csv_data = np.genfromtxt('drawings/4F_straight_no_EV.csv', delimiter=',', dtype=None, encoding='UTF-8') # -> 닫힌공간 실패, island 문제

    # csv test cases
    # csv_data = np.genfromtxt('testcases/diagonal.csv', delimiter=',', dtype=None, encoding='UTF-8') # -> 닫힌공간 실패, 세갈래 미구현
    # csv_data = np.genfromtxt('testcases/h-shaped.csv', delimiter=',', dtype=None, encoding='UTF-8')
    # csv_data = np.genfromtxt('testcases/square.csv', delimiter=',', dtype=None, encoding='UTF-8') # -> island 문제

    # classifying elements and obtaining constraints of drawing
    min_x, min_y, max_x, max_y = object_loader.classify_data(csv_data, wall_line_list, door_line_list, arc_list,
                                                             door_block_list)
    # object_loader.door_integrator(door_block_list, door_line_list, arc_list)
    # test for all of csv data
    print("[wall lines]: " + str(len(wall_line_list)))
    print("[door lines]: " + str(len(door_line_list)))
    print("[arcs]: " + str(len(arc_list)))
    print("[door blocks]: " + str(len(door_block_list)))

    # for i in range(len(wall_line_list)):
    #     print(wall_line_list[i])

    """##### (2) 마주보는 벽체 탐색 단계 #####"""
    line_equations = []
    wall_pairs = []
    hall_pairs = []

    ### <동일 선상의 직선 분류> classifying same equations using linked list ###
    processor.classify_same_wall_lines(wall_line_list, line_equations)
    # TEST FOR SAME LINE EQUATION
    # print("[line_equations]: " + str(len(line_equations)))
    # for i in range(len(line_equations)):
    #     line_equations[i].print_all()
    # print("")

    ##### "닫힌 구간 확인" #####
    enclosings, door_sills = inner_line_harvester.get_enclosings(line_equations, door_block_list)
    # print("ENCLOSINGS")
    # for i in range(len(enclosings)):
    #     enclosings[i].print_all()

    ##### "내측 벽면 추출" #####
    # inner_lines = enclosings # 지워 지워 지워
    inner_lines = inner_line_harvester.get_inner_lines(line_equations, enclosings, door_sills)
    # print("INNER LINES")
    # for i in range(len(inner_lines)):
    #     inner_lines[i].print_all()

    ##### "복도벽선 페어 생성" #####
    hall_pairs = hallway_maker.get_hall_pairs(inner_lines)
    # print("HALL PAIRS")
    # for i in range(len(hall_pairs)):
    #     print(hall_pairs[i])

    ##### "복도트리 생성" #####
    crossed_halls = hallway_maker.get_crossed_hall(hall_pairs)
    # print("CROSSED HALLS")
    # for i in range(len(crossed_halls)):
    #     print(crossed_halls[i])

    ##### "복도 분지" #####
    hall_trees = []
    hall_trees = hallway_maker.break_pairs(crossed_halls, inner_lines)
    # print("HALL TREES")
    # for i in range(len(hall_trees)):
    #     print(str(i)+":", hall_trees[i][0])
    #     print(hall_trees[i][1])
    #     hall_trees[i][2].print_all()

    ##### "실내그래프 생성" #####
    indoor_graphs = indoor_graph.build_graph(hall_trees)
    # print("INDOOR GRAPH DFS")
    # for i in range(len(indoor_graphs)):
    #     print("indoor_graph["+str(i)+"]")
    #     indoor_graphs[i].dfs()

    # 기준점 두개 이상일때의 그래프 생성 (이전 방법은 22.12.06 버전)
    # 1. 복도 트리 구성, hall_tree = {기준점, 소교차점 리스트, 교차하는 hall_pair1, hall_pair2}
    # 2. hall_tree들 저장
    # 3. 각 hall_tree 별 복도 분지
    # 4. 분지된 hall_tree 내 hall_pair들에 벽선들 붙이기
    # 5. 분지된 hall_tree들의 hall_pair들끼리 비교하면서 중복되면 그래프 합성

    # drawing test
    visualizer.drawing_test(MAGNIFICATION, line_equations, door_line_list, door_block_list, door_sills, inner_lines,
                            hall_pairs, crossed_halls, hall_trees, max_x, max_y)

    # indoor_graph.get_nodes() 테스트
    # print("indoor_graph.get_nodes() test: (len of indoor_graphs)", len(indoor_graphs))
    hall_nodes, hall_nodes_reverse, end_nodes = indoor_graph.get_nodes(indoor_graphs[0])
