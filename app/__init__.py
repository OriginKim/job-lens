import sys
import types

if "onnxruntime" not in sys.modules:
    sys.modules["onnxruntime"] = types.ModuleType("onnxruntime")
