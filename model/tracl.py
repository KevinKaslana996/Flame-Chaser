import os
import sys
import csv
import traci
from sumolib import checkBinary

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("请声明环境变量 'SUMO_HOME'")

SUMO_CONFIG = "E:/trajectory_prediction/data/sumo.sumocfg"
USE_GUI = True
OUTPUT_CSV = "vehicle_features.csv"
STEP_INTERVAL = 1

def extract_vehicle_features(veh_id, step):
    """提取单辆车的所有特征"""
    features = {}

    features['vehicle_id'] = veh_id
    features['timestep'] = step

    try:
        x, y = traci.vehicle.getPosition(veh_id)
        features['x'] = x
        features['y'] = y
    except:
        features['x'], features['y'] = None, None

    try:
        features['speed'] = traci.vehicle.getSpeed(veh_id)
    except:
        features['speed'] = None

    try:
        features['acceleration'] = traci.vehicle.getAcceleration(veh_id)
    except:
        features['acceleration'] = None

    try:
        features['angle'] = traci.vehicle.getAngle(veh_id)
    except:
        features['angle'] = None

    try:
        features['road_id'] = traci.vehicle.getRoadID(veh_id)
    except:
        features['road_id'] = None

    try:
        features['lane_id'] = traci.vehicle.getLaneID(veh_id)
    except:
        features['lane_id'] = None

    try:
        features['lane_index'] = traci.vehicle.getLaneIndex(veh_id)
    except:
        features['lane_index'] = None

    try:
        features['allowed_speed'] = traci.vehicle.getAllowedSpeed(veh_id)
    except:
        features['allowed_speed'] = None

    try:
        route = traci.vehicle.getRoute(veh_id)
        features['route'] = ';'.join(route)
        features['route_length'] = len(route)
    except:
        features['route'] = None
        features['route_length'] = None

    try:
        features['route_index'] = traci.vehicle.getRouteIndex(veh_id)
    except:
        features['route_index'] = None

    try:
        type_id = traci.vehicle.getTypeID(veh_id)
        features['type_id'] = type_id

        features['length'] = traci.vehicletype.getLength(type_id)
        features['max_speed'] = traci.vehicletype.getMaxSpeed(type_id)
        features['max_accel'] = traci.vehicletype.getAccel(type_id)
        features['max_decel'] = traci.vehicletype.getDecel(type_id)
        features['tau'] = traci.vehicletype.getTau(type_id)
        features['vehicle_class'] = traci.vehicletype.getVehicleClass(type_id)
    except:
        features['type_id'] = None
        features['length'] = None
        features['max_speed'] = None
        features['max_accel'] = None
        features['max_decel'] = None
        features['tau'] = None
        features['vehicle_class'] = None

    try:
        leader = traci.vehicle.getLeader(veh_id, distance=100.0)
        if leader:
            leader_id, distance_to_leader = leader
            features['leader_id'] = leader_id
            features['distance_to_leader'] = distance_to_leader
        else:
            features['leader_id'] = None
            features['distance_to_leader'] = None
    except:
        features['leader_id'] = None
        features['distance_to_leader'] = None

    return features


def run_simulation_and_collect():

    sumo_binary = checkBinary('sumo-gui') if USE_GUI else checkBinary('sumo')
    traci.start([sumo_binary, "-c", SUMO_CONFIG])

    csv_file = open(OUTPUT_CSV, 'w', newline='', encoding='utf-8')
    fieldnames = [
        'vehicle_id', 'timestep',
        'x', 'y', 'speed', 'acceleration', 'angle',
        'road_id', 'lane_id', 'lane_index', 'allowed_speed',
        'route', 'route_length', 'route_index',
        'type_id', 'length', 'max_speed', 'max_accel', 'max_decel', 'tau', 'vehicle_class',
        'leader_id', 'distance_to_leader'
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    step = 0
    print("开始仿真数据采集...")

    # 仿真主循环
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # 按间隔记录数据
        if step % STEP_INTERVAL == 0:
            vehicle_ids = traci.vehicle.getIDList()

            for veh_id in vehicle_ids:
                features = extract_vehicle_features(veh_id, step)
                writer.writerow(features)

            if step % 100 == 0:
                print(f"  时间步 {step}: 已记录 {len(vehicle_ids)} 辆车")

        step += 1

    traci.close()
    csv_file.close()
    print(f"数据采集完成！共 {step} 个时间步，结果保存至 {OUTPUT_CSV}")


def run_simulation_with_subscription():
    sumo_binary = checkBinary('sumo-gui') if USE_GUI else checkBinary('sumo')
    traci.start([sumo_binary, "-c", SUMO_CONFIG])

    csv_file = open(OUTPUT_CSV, 'w', newline='', encoding='utf-8')
    fieldnames = ['vehicle_id', 'timestep', 'x', 'y', 'speed', 'acceleration', 'angle',
                  'road_id', 'lane_id', 'route', 'type_id', 'leader_id', 'distance_to_leader']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    traci.simulation.subscribeContext(
        "",  # 空字符串表示全局范围
        traci.vehicle.DOMAIN_ID,  # 订阅车辆域
        10000.0,  # 覆盖半径（足够大以包含所有车辆）
        [
            traci.var.POSITION,
            traci.var.SPEED,
            traci.var.ACCELERATION,
            traci.var.ANGLE,
            traci.var.ROAD_ID,
            traci.var.LANE_ID,
            traci.var.ROUTE,
            traci.var.TYPE,
        ]
    )

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if step % STEP_INTERVAL == 0:
            results = traci.simulation.getContextSubscriptionResults("")
            if results:
                for veh_id, data in results.items():
                    row = {
                        'vehicle_id': veh_id,
                        'timestep': step,
                        'x': data[traci.var.POSITION][0] if traci.var.POSITION in data else None,
                        'y': data[traci.var.POSITION][1] if traci.var.POSITION in data else None,
                        'speed': data.get(traci.var.SPEED),
                        'acceleration': data.get(traci.var.ACCELERATION),
                        'angle': data.get(traci.var.ANGLE),
                        'road_id': data.get(traci.var.ROAD_ID),
                        'lane_id': data.get(traci.var.LANE_ID),
                        'route': ';'.join(data.get(traci.var.ROUTE, [])),
                        'type_id': data.get(traci.var.TYPE),
                        'leader_id': None,
                        'distance_to_leader': None,
                    }
                    writer.writerow(row)

        step += 1

    traci.close()
    csv_file.close()
    print(f"订阅模式采集完成，结果保存至 {OUTPUT_CSV}")


if __name__ == "__main__":

    #run_simulation_and_collect()
    
    run_simulation_with_subscription()