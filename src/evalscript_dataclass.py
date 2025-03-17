from __future__ import annotations

from pydantic import BaseModel, Field


class InputDefinition(BaseModel):
    """
    Represents an item in the `input` list of the Evalscript's setup.
    Example:
      input: [
        {
          "bands": ["B02", "B03", "B04"],
          "units": "DN"
        }
      ]
    """

    bands: list[str] = Field(..., description="List of band names.")
    units: str | list[str] = Field(None, description="Unit(s) for each band.")


class OutputDefinition(BaseModel):
    """
    Represents a single output object.
    Can handle single or multiple outputs.
    Example:
      output: [
        {
          "id": "default",
          "bands": 3,
          "sample_type": "UINT8"
        }
      ]
    """

    id: str | None = Field("default", description="Identifier for this output object.")
    bands: int = Field(..., description="Number of bands.")
    sample_type: str | None = Field(
        "AUTO", description="SampleType (e.g., UINT8, UINT16, FLOAT32, AUTO)."
    )
    nodata_value: float | None = Field(None, description="Optional no-data value.")


class Setup(BaseModel):
    """
    Represents the `setup` function of the evalscript (its return object).
    Mosaicking is optional but included here for completeness.
    """

    input: list[InputDefinition]
    output: OutputDefinition | list[OutputDefinition]
    mosaicking: str | None = Field(
        "SIMPLE", description="Mosaicking method: SIMPLE|ORBIT|TILE"
    )

    def _render_input_js(self) -> str:
        """Render the input part of the JavaScript setup."""
        inputs_js = []
        for inp in self.input:
            band_str = f"bands: {inp.bands}"
            if inp.units is not None:
                if isinstance(inp.units, list):
                    units_val = f'["{"\",\"".join(inp.units)}"]'
                else:
                    units_val = f'"{inp.units}"'
                band_str += f", units: {units_val}"
            inputs_js.append("{" + band_str + "}")
        return ", ".join(inputs_js)

    def _render_output_js(self) -> str:
        """Render the output part of the JavaScript setup."""
        if isinstance(self.output, list):
            outputs_js = []
            for outp in self.output:
                out_props = [f'id: "{outp.id}"', f"bands: {outp.bands}"]
                if outp.sample_type:
                    out_props.append(f'sampleType: "{outp.sample_type}"')
                if outp.nodata_value is not None:
                    out_props.append(f"nodataValue: {outp.nodata_value}")
                outputs_js.append("{" + ", ".join(out_props) + "}")
            return f"[{', '.join(outputs_js)}]"

        outp = self.output
        out_props = [f"bands: {outp.bands}"]
        if outp.id != "default":
            out_props.insert(0, f'id: "{outp.id}"')
        if outp.sample_type:
            out_props.append(f'sampleType: "{outp.sample_type}"')
        if outp.nodata_value is not None:
            out_props.append(f"nodataValue: {outp.nodata_value}")
        return "{" + ", ".join(out_props) + "}"

    def render_setup(self) -> str:
        """
        Renders the JavaScript `setup()` function.
        The exact structure depends on whether `output` is a single dict or a list of
        dicts.
        """
        input_str = self._render_input_js()
        output_str = self._render_output_js()
        mosaicking_str = (
            f',\n            mosaicking: "{self.mosaicking}"' if self.mosaicking else ""
        )

        return (
            "function setup() {\n"
            "    return {\n"
            f"        input: [{input_str}],\n"
            f"        output: {output_str}{mosaicking_str}\n"
            "    };\n"
            "}\n"
        )


class EvalFunctions(BaseModel):
    """
    Holds the optional JS code for pre_process_scenes, evaluate_pixel,
    update_output, etc. Each is a string containing raw JavaScript code.
    """

    pre_process_scenes: str | None = None
    evaluate_pixel: str = Field(
        ..., description="Core evaluatePixel function as JavaScript."
    )
    update_output: str | None = None
    update_output_metadata: str | None = None

    def render_preprocess(self) -> str:
        if self.pre_process_scenes:
            return (
                "function preProcessScenes(collections) {\n"
                f"{self.pre_process_scenes}\n"
                "}\n"
            )
        return ""

    def render_evaluate_pixel(self) -> str:
        return (
            "function evaluatePixel(samples, scenes, inputMetadata, "
            f"customData, outputMetadata) {{\n{self.evaluate_pixel}\n}}\n"
        )

    def render_update_output(self) -> str:
        if self.update_output:
            return (
                "function updateOutput(output, collection) {\n"
                f"{self.update_output}\n"
                "}\n"
            )
        return ""

    def render_update_output_metadata(self) -> str:
        if self.update_output_metadata:
            return (
                "function updateOutputMetadata(scenes, inputMetadata, "
                f"outputMetadata) {{\n{self.update_output_metadata}\n}}\n"
            )
        return ""


class EvalScriptV3(BaseModel):
    """
    The master Pydantic model that ties everything together.
    """

    setup_obj: Setup
    eval_functions: EvalFunctions

    def generate_evalscript(self) -> str:
        """
        Generate the complete evalscript in JavaScript.
        """
        setup_js = self.setup_obj.render_setup()
        preproc_js = self.eval_functions.render_preprocess()
        evalpixel_js = self.eval_functions.render_evaluate_pixel()
        updateoutput_js = self.eval_functions.render_update_output()
        updateoutputmeta_js = self.eval_functions.render_update_output_metadata()

        return (
            "//VERSION=3\n"
            f"{setup_js}\n"
            f"{preproc_js}"
            f"{evalpixel_js}"
            f"{updateoutput_js}"
            f"{updateoutputmeta_js}"
        )
