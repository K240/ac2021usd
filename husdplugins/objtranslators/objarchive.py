import hou
import husd
from pxr import Usd, UsdGeom, Sdf

class ObjArchiveTranslator(husd.objtranslator.Translator):

    def shouldTranslateNode(self):
        if not self._node.isDisplayFlagSet():
            return False
        if self._node.parm('tdisplay').eval() and \
                not self._node.parm('display').eval():
            return False
        return True

    def primType(self):
        return 'Xform'

    def populatePrim(self, prim, referenced_node_prim_paths, force_active):
        if self._node.parm('filename').evalAsString():
            # ObjファイルをPayloadに登録する
            prim.GetPayloads().AddPayload(assetPath=self._node.parm('filename').evalAsString())
            # assetNameアトリビュートをPrimアトリビュートに登録する
            self.populateAttr(prim.CreateAttribute('assetName', Sdf.ValueTypeNames.String), self._node.parm('assetName'))
            # versionアトリビュートをPrimアトリビュートに登録する
            self.populateAttr(prim.CreateAttribute('assetVersion', Sdf.ValueTypeNames.String), self._node.parm('version'))
        if not force_active:
            if not self._node.isDisplayFlagSet():
                prim.SetActive(False)
            elif self._node.parm('tdisplay').eval():
                if self._node.parm('display').isTimeDependent():
                    t = Usd.TimeCode(hou.frame())
                else:
                    t = Usd.TimeCode.Default()
                api = UsdGeom.Imageable(prim)
                if self._node.parm('display').eval():
                    api.MakeVisible(t)
                else:
                    api.MakeInvisible(t)

def registerTranslators(manager):
    manager.registerTranslator('ObjArchive', ObjArchiveTranslator)
