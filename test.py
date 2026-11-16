"""租户自定义工具关联读取；前端专用 AgentID 与乐观锁 Revision。"""
import pytest
from api.secagent import frontend_contract_helpers as F

pytestmark = [pytest.mark.patrol]


def assert_binding(binding, agent_id):
    assert binding.get("AgentID") == agent_id, binding
    assert binding.get("TenantToolPolicy") in {"allow", "deny"}, binding
    F.nonnegative(binding.get("Revision", 0), binding)
    for key in ("ToolPackageIDs", "ToolIDs"):
        values = binding.get(key, [])
        assert isinstance(values, list) and all(isinstance(value, str) and value for value in values), binding
        assert len(values) == len(set(values)), binding
    F.items(binding, "ToolPackages")
    F.items(binding, "Tools")


@pytest.mark.P1
@pytest.mark.read
@pytest.mark.private
@pytest.mark.online
class TestTenantBindingsRead:
    def test_get_binding(self, get_env):
        result = F.post(get_env, "ListMasAgent", {"CurrentPage": 1, "PageSize": 100})
        agents = F.items(result)
        assert agents, ("前置数据不足：没有智能体", result)
        agent_id = agents[0]["RecordUUID"]
        binding = F.post(get_env, "GetAgentTenantToolBindings", {"AgentID": agent_id})
        assert_binding(binding, agent_id)

