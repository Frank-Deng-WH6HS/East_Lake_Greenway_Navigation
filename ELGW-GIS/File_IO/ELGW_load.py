#ELGW-GIS东湖绿道路网数据shp导入

#作者: Frank-Deng-WH6HS <enter_the_dragon@foxmail.com>

#引用的开源代码库项目: 
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

#从ESRI Shapefile文件中导入东湖绿道部分路段路网
def load_path_from_shp(): 
    elgw_filepath = os.sep.join([
        __script_dir__, os.pardir, "Data_Built-in", "ELGW_Path", "ELGW_Main_2D_EPSG_32649.shp"
    ]); 
    elgw_path_minor = shpf.Reader(elgw_filepath); 
    elgw_path_minor_shplgeo = [
        shplgeo.LineString(sgm.points) for sgm in elgw_path_minor.shapes()
    ]; 
    elgw_path_minor_prop = elgw_path_minor.records(); 
    return((elgw_path_minor_shplgeo, elgw_path_minor_prop)); 
