"""
Demo Items 接口测试
"""
import pytest


@pytest.mark.asyncio
async def test_list_items(client):
    """测试获取 Item 列表"""
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_item(client):
    """测试创建 Item"""
    item_data = {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "price": 99.99,
        "is_active": True,
        "category": "electronics",
    }
    response = await client.post("/api/v1/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data

