import hazelcast
import time


def member_added(member):
    print("Member added: {}".format(member.member))


def member_removed(member):
    print("Member removed: {}".format(member.member))


if __name__ == "__main__":
    client = hazelcast.HazelcastClient()
    client.cluster.add_listener(member_added, member_removed, True)

    # Add/Remove member now to see the listeners in action
    time.sleep(100)
    client.shutdown()
