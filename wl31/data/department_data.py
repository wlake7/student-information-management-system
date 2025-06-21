# wl31/data/department_data.py

DEPARTMENTS = {
    "计算机学院": ["计算机科学与技术", "软件工程", "网络工程", "物联网工程", "数据科学与大数据技术"],
    "外国语学院": ["英语", "日语", "法语", "德语", "商务英语"],
    "经济管理学院": ["工商管理", "市场营销", "会计学", "财务管理", "国际经济与贸易"],
    "艺术设计学院": ["视觉传达设计", "环境设计", "产品设计", "服装与服饰设计", "数字媒体艺术"],
    "机械工程学院": ["机械设计制造及其自动化", "材料成型及控制工程", "车辆工程", "机械电子工程"]
}

def get_departments():
    """返回所有学院的列表"""
    return list(DEPARTMENTS.keys())

def get_majors_by_department(department):
    """根据学院名称返回对应的专业列表"""
    return DEPARTMENTS.get(department, [])