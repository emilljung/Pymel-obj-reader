import pymel.core as pm
import pymel.core.nodetypes as nt
import shutil

#Window -> Settings/Preferences -> Plug-in Manager -> Check Loaded next to "objExport.mll"
#File -> Export All/Selection and you should be able to choose "OBJexport" in Files of type

def getSelected():
    #Only put the objects which are nt.Transform AND are nt.Mesh
    allSelected = [ obj.getShape() for obj in pm.ls(selection=True) if isinstance(obj, nt.Transform) and isinstance(obj.getShape(), nt.Mesh) ]
    return allSelected    #Returns a list of pymel.core.nodetypes.Mesh
    
def getAll():
    allObj = pm.ls(geometry=True) #Returns a list of all geometry (even nurbs)
    for x in allObj:
        if type(x) is not nt.Mesh:
            allObj.remove(x)
    return allObj #Returns a list of pymel.core.nodetypes.Mesh
    
def writeMeshListToFile(meshList, spaceType, grouping, materials, myFile):
    nrOfPos = 0
    nrOfUVs = 0
    nrOfNor = 0
    for obj in meshList:
        #Triangulate mesh so that the object(s) can be imported correctly later
        pm.polyTriangulate(obj)
        
        myFile.write('g default\r\n') #I don't know what this is for
        #Save all positions for the mesh 
        for v in obj.vtx:
            pos = v.getPosition(space=spaceType)
            myFile.write('v ' + str(round(pos.x,6)) +' '+ str(round(pos.y,6)) +' '+ str(round(pos.z,6))+'\r\n') 
            
        #Save all UVs for the mesh
        U,V = obj.getUVs()
        UVs = zip(U,V)
        for uv in UVs:
            myFile.write('vt ' + str(round(uv[0],6)) +' '+ str(round(uv[1],6))+'\r\n')
        
        #Save all normals for the mesh
        for n in obj.getNormals():
            myFile.write('vn ' + str(round(n.x,6)) +' '+ str(round(n.y,6)) +' '+ str(round(n.z,6))+'\r\n')
            
        #Write this here if grouping is true
        if grouping is True:
            myFile.write('g ' + obj +'\r\n')
        
        #Write this here if materials is true
        if materials is True and len(obj.shadingGroups()) > 0:
            myFile.write('usemtl ' + obj.shadingGroups()[0] + '\r\n')
            
        #Match all values so that they together build triangles
        #Triangles are described like v/vt/vn v/vt/vn v/vt/vn
        for f in obj.faces:
            v_idxs = [ v+1 + nrOfPos for v in f.getVertices() ]
            t_idxs = [ f.getUVIndex(i)+1 + nrOfUVs for i in range(3) ]
            n_idxs = [ f.normalIndex(i)+1  + nrOfNor for i in range(3) ]
            s = 'f ' + str(v_idxs[0]) + '/' + str(t_idxs[0]) + '/' + str(n_idxs[0]) + ' '
            s += str(v_idxs[1]) + '/' + str(t_idxs[1]) + '/' + str(n_idxs[1]) + ' '
            s += str(v_idxs[2]) + '/' + str(t_idxs[2]) + '/' + str(n_idxs[2])
            myFile.write(s +'\r\n') #The result here describes a triangle is a triangle
        myFile.write('\r\n') #To separate info from this mesh from the next one
        
        #Increase the nr of pos, uvs & normals for the next mesh
        nrOfPos += len(obj.vtx)
        nrOfUVs += len(UVs)
        nrOfNor += len(obj.getNormals())

def createOBJFile(meshList, spaceType, grouping, materials, fileName, path):
    try:
        #Creates file if it doesn't exist
        myFile = open(path + fileName + '.obj', 'w')
        myFile.write('mtllib ' + fileName + '.mtl\r\n')
        writeMeshListToFile(meshList, spaceType, grouping, materials, myFile)
    except Exception, e:
        print "Error writing to file:" + str(e)
    finally:
        myFile.close()
        
def createMTLFile(meshList, fileName, path):
    try:
        #Creates file if it doesn't exist
        myFile = open(path + fileName + '.mtl', 'w')
        writeToMTL(meshList, myFile)
    except Exception, e:
        print "Error writing to file:" + str(e)
    finally:
        myFile.close()
        
def writeToMTL(meshList, myFile):
    uniqueValues = []
    for obj in meshList:
        if len(obj.shadingGroups()) > 0:
            values = [] #Put values in here and compare with uniqueValues
            
            sg = obj.shadingGroups()[0] #pymel.core.nodetypes.ShadingEngine
            values.append('newmtl ' + sg + '\r\n')
            
            values.append('illum 4\r\n')    #Illumination model
            
            material = sg.listConnections(source=True, destination=True, type=nt.Lambert)[0]
            
            c = material.getColor() #Diffuse
            values.append('Kd '+ str(round(c[0],2)) +' '+ str(round(c[1],2)) +' '+ str(round(c[2],2)) +'\r\n')
            
            c = material.getAmbientColor() #Ambient
            values.append('Ka '+ str(round(c[0],2)) +' '+ str(round(c[1],2)) +' '+ str(round(c[2],2)) +'\r\n')
            
            values.append('Tf 1.00 1.00 1.00\r\n') #The transparency of the material
            
            #TextureName
            f = material.color.listConnections(type=nt.File)
            if len(f) > 0:
                values.append('map_Kd ' + f[0].fileTextureName.get().split('/')[-1] + '\r\n')
             
            #Refraction
            values.append('Ni ' + str(round(material.getRefractiveIndex(),2)) + '\r\n')
			
			#Not all meshes have specular
            if (material.hasAttr('specularColor')):
                c = material.getSpecularColor() #Specular
                values.append('Ks '+ str(round(c[0],2)) +' '+ str(round(c[1],2)) +' '+ str(round(c[2],2)) +'\r\n')
                        
            if values not in uniqueValues:
                uniqueValues.append(values)
                for x in values:    #values is emptied after this
                    myFile.write(x)

def copyTextureFiles(meshList, destination):
    uniqueTextures = []
    for obj in meshList:
        if len(obj.shadingGroups()) > 0:   
            textures = ''
            sg = obj.shadingGroups()[0] #pymel.core.nodetypes.ShadingEngine
            
            material = sg.listConnections(source=True, destination=True, type=nt.Lambert)[0]            
            
            #TextureName
            f = material.color.listConnections(type=nt.File)
            if len(f) > 0:
                textures = f[0].fileTextureName.get()

            if textures not in uniqueTextures and textures != '':
                uniqueTextures.append(textures)
    for x in uniqueTextures:    # Copy the texture files to save destination
        shutil.copy(x, destination)

def doSomething(onlySelection, groups, materials, typeOfCoords, path, fileName):
    meshList = getAll()
    if onlySelection is True:
        meshList = getSelected()
    createOBJFile(meshList, typeOfCoords, groups, materials, fileName, path)
    
    if materials is True:
        #The info from all meshes are supposed to be included even if you only export 1 mesh.
        createMTLFile(getAll(), fileName, path)
        copyTextureFiles(getAll(), path)