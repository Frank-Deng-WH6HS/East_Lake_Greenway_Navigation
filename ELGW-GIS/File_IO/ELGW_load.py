#ELGW-GIS东湖绿道路网数据shp导入

#作者: Frank-Deng-WH6HS <enter_the_dragon@foxmail.com>

#引用的第三方python开源代码库项目: 
#   PyShp - MIT License
#   shapely - BSD License

#操作目录和文件
import os; __script_dir__ = os.path.dirname(__file__); 
#导入shp
import shapefile as shpf; 
#处理几何信息
import shapely; 
import shapely.geometry as shplgeo, shapely.affinity as shplaffin; 
import shapely.ops as shplops; 
#操作数组
import numpy as np; 
from functools import reduce; 

#按照下标对list或者tuple进行切分
def partition_indexed(ls: list or tuple, idx_prtn: list or tuple) -> tuple: 
    idx_prtn_tail = list(idx_prtn[1: ]); 
    idx_prtn_tail.append(None); 
    ls_prtn = tuple(tuple(ls[idx_head: idx_tail]) 
        for idx_head, idx_tail in zip(idx_prtn, idx_prtn_tail)
    ); 
    return(ls_prtn); 

#定义从shp空间数据文件提取所得的几何特征和属性特征组合形成的对象
class AttributiveGeometry(): 
    
    #初始化(导入shp文件中的各种属性)
    def __init__(self, shp_path): 
        #打开shp文件
        shpf_obj = shpf.Reader(shp_path); 
        #获取shp几何类型属性("POINT", "POLYLINE", "POLYGON")
        shpf_fig_type = shpf_obj.shapeType
        if shpf_fig_type in {0, 31}: 
            self.shapeTypeName = shpf.SHAPETYPE_LOOKUP[shpf_fig_type]; 
        else: 
            self.shapeTypeName = shpf.SHAPETYPE_LOOKUP[shpf_fig_type % 10]; 
            #判断shp文件是否具有M(转向)和Z(高程)数据
            self.has_m = bool(shpf_fig_type // 10 == 2); 
            self.has_z = bool(shpf_fig_type // 10 == 1); 
        #读取几何属性
        #获取每个几何实体的所有部分的顶点坐标
        shpf_obj_vertex_coords = tuple(
            tuple(entity.points) for entity in shpf_obj.shapes()
        ); 
        shpf_obj_prtn_info = tuple(
            tuple(entity.parts) for entity in shpf_obj.shapes()
        ); 
        if self.shapeTypeName == "POINT": 
            shplgeo_single_part = "Point"; 
            shplgeo_multiple_part = "MultiPoint"; 
        elif self.shapeTypeName == "POLYLINE": 
            shplgeo_single_part = "LineString"; 
            shplgeo_multiple_part = "MultiLineString"; 
        else: 
            #尚未实现对多边形和点云shp的解析功能, 如遇此类shp将报错
            raise shpf.ShapefileException; 
        #如果一个几何实体包含多个部分, 则每个部分分别显示
        shpf_obj_single_part_coords = tuple(
            partition_indexed(vrtx_coord, idx_prtn) \
            for vrtx_coord, idx_prtn \
            in zip(shpf_obj_vertex_coords, shpf_obj_prtn_info)
        ); 
        #整理几何信息
        shplgeo_single_part = eval(
            "\x2E".join([shplgeo.__name__, shplgeo_single_part])
        ); 
        shplgeo_multiple_part = eval(
            "\x2E".join([shplgeo.__name__, shplgeo_multiple_part])
        ); 
        shpf_obj_single_part = tuple(
            tuple(
                shplgeo_single_part(prt) for prt in entity
            ) for entity in shpf_obj_single_part_coords
        ); 
        shpf_obj_multiple_part = tuple(
            shplgeo_multiple_part(entity) for entity in shpf_obj_single_part
        ); 
        self.geometry = shpf_obj_multiple_part
        #整理属性信息, 使之易于检索
        shpf_obj_fld = shpf_obj.fields; 
        shpf_obj_entity = tuple(
            tuple(entity) for entity in shpf_obj.records()
        ); 
        shpf_obj_entity = np.array(shpf_obj_entity).transpose(); 
        shpf_obj_prop = dict(); 
        for idx, fld in enumerate(shpf_obj_fld[1: ]): 
            shpf_obj_prop[fld[0]] = shpf_obj_entity[idx, :]; 
        self.attribute = shpf_obj_prop
        #完成读取后关闭文件, 解除占用. 
        shpf_obj.close(); 


#从ESRI Shapefile文件中导入东湖绿道部分路段路网
def elgw_scenic_path_load(): 
    elgw_filepath = os.sep.join([
        __script_dir__, os.pardir, "Data_Built-in", "ELGW_Path", 
        "ELGW_Main_2D_EPSG_32649.shp"
    ]); 
    return(AttributiveGeometry(elgw_filepath)); 
