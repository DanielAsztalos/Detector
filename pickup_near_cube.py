import cozmo

def pickup_and_put_on_ground(robot: cozmo.robot.Robot):
    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
    lookaround.stop()

    if len(cubes) > 0:
        target = cubes[0]
        robot.pickup_object(target, num_retries=3).wait_for_completed()
        robot.place_object_on_ground_here(target, num_retries=3).wait_for_completed()
    else:
        print("No cubes found")
