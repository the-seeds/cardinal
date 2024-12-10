from cardinal import AutoGraphStorage
from RagPanel.utils.graph_utils import Entity, Relation

def test_neo4j():
    storage = AutoGraphStorage("test_db")
    storage.destroy()

    # 测试节点插入
    entity_keys = ["entity1", "entity2"]
    entities = [
        Entity(name="Entity 1", type="Type A", desc="This is entity 1."),
        Entity(name="Entity 2", type="Type B", desc="This is entity 2."),
    ]
    storage.insert_node(entity_keys, entities)

    # 查询节点
    entity1 = storage.query_node("entity1")
    assert entity1 is not None, "Entity 1 should exist"
    # 手动从 Node 对象中提取属性
    assert entity1["name"] == "Entity 1" and entity1["type"] == "Type A" and entity1["desc"] == "This is entity 1."

    entity2 = storage.query_node("entity2")
    assert entity2 is not None, "Entity 2 should exist"
    # 手动从 Node 对象中提取属性
    assert entity2["name"] == "Entity 2" and entity2["type"] == "Type B" and entity2["desc"] == "This is entity 2."

    # 测试边插入
    relation_keys_head = ["entity1"]
    relation_keys_tail = ["entity2"]
    relations = [
        Relation(head="entity1", tail="entity2", desc="Connected", strength=1).model_dump_json()
    ]
    storage.insert_edge(relation_keys_head, relation_keys_tail, relations)

    # 查询边
    relation = storage.query_edge("entity1", "entity2")
    assert relation is not None, "Relation from entity1 to entity2 should exist"
    import json
    relation = json.loads(relation["properties"])
    assert relation["desc"] == "Connected" and relation["strength"] == 1

    # 查询节点的所有出边
    entity1_relations = storage.query_node_edges("entity1")
    assert entity1_relations is not None and len(entity1_relations) == 1, "Entity 1 should have one outgoing relation"

    # 测试 exists 功能
    assert storage.exists(), "Graph storage should exist"

    # 测试 destroy 功能
    storage.destroy()

    # 验证清理是否成功
    entity1_after_destroy = storage.query_node("entity1")
    assert entity1_after_destroy is None, "Entity 1 should no longer exist after destroy"

    entity2_after_destroy = storage.query_node("entity2")
    assert entity2_after_destroy is None, "Entity 2 should no longer exist after destroy"

    print("All tests passed!")
