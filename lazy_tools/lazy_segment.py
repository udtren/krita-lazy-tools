"""
Florence-2 + SAM2 Segmentation Pipeline

This script demonstrates the workflow of:
1. Using Florence-2 for caption-to-phrase grounding (finding objects in image)
2. Using SAM2 to generate precise segmentation masks from bounding boxes
3. Creating red mask overlay visualization

Can be used as both a standalone script and imported module.
"""

import os
import sys
import argparse
import numpy as np
import torch
from PIL import Image, ImageDraw
import cv2
from transformers import AutoProcessor, AutoModelForCausalLM
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


class FloSAM2Pipeline:
    """Florence-2 + SAM2 segmentation pipeline."""

    def __init__(self, sam2_model_key="base_plus"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Store selected model
        self.sam2_model_key = sam2_model_key

        # Set up local model directory
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.models_dir, exist_ok=True)

        # Florence-2 model path - using base model to avoid flash attention issues
        self.florence_model_path = os.path.join(self.models_dir, "florence-2-large-ft")

        # Initialize Florence-2
        self.florence_model = None
        self.florence_processor = None

        # Initialize SAM2
        self.sam2_predictor = None

        self._load_models()

    def _load_models(self):
        """Load Florence-2 and SAM2 models."""
        try:
            print(f"Loading Florence-2 model to: {self.florence_model_path}")

            # Check if model already exists locally
            if os.path.exists(self.florence_model_path) and os.listdir(
                self.florence_model_path
            ):
                print("📁 Loading Florence-2 from local directory...")
                # Load from local directory
                self.florence_processor = AutoProcessor.from_pretrained(
                    self.florence_model_path,
                    trust_remote_code=True,
                    local_files_only=True,
                )
                self.florence_model = AutoModelForCausalLM.from_pretrained(
                    self.florence_model_path,
                    torch_dtype=(
                        torch.float32 if self.device == "cpu" else torch.float16
                    ),
                    trust_remote_code=True,
                    local_files_only=True,
                    attn_implementation="eager",  # Fix for _supports_sdpa error
                ).to(self.device)
            else:
                print("🌐 Downloading Florence-2 from Hugging Face...")
                # Download and save to local directory
                self.florence_processor = AutoProcessor.from_pretrained(
                    "microsoft/Florence-2-large-ft",
                    trust_remote_code=True,
                    cache_dir=self.models_dir,
                )
                self.florence_model = AutoModelForCausalLM.from_pretrained(
                    "microsoft/Florence-2-large-ft",
                    torch_dtype=(
                        torch.float32 if self.device == "cpu" else torch.float16
                    ),
                    trust_remote_code=True,
                    cache_dir=self.models_dir,
                    attn_implementation="eager",  # Fix for _supports_sdpa error
                ).to(self.device)

                # Save to local directory for future use
                print(
                    f"💾 Saving Florence-2 to local directory: {self.florence_model_path}"
                )
                self.florence_processor.save_pretrained(self.florence_model_path)
                self.florence_model.save_pretrained(self.florence_model_path)

            print("✅ Florence-2 loaded successfully")

        except Exception as e:
            print(f"❌ Error loading Florence-2: {e}")
            print("🔧 Trying alternative loading method...")

            # Fallback: Try loading with different parameters
            try:
                self.florence_processor = AutoProcessor.from_pretrained(
                    "microsoft/Florence-2-large-ft", trust_remote_code=True
                )

                # Load model with explicit configuration to avoid SDPA issues
                self.florence_model = AutoModelForCausalLM.from_pretrained(
                    "microsoft/Florence-2-large-ft",
                    torch_dtype=torch.float32,  # Use float32 instead of float16
                    trust_remote_code=True,
                    device_map="auto" if self.device == "cuda" else None,
                    attn_implementation="eager",
                )

                if self.device == "cpu":
                    self.florence_model = self.florence_model.to(self.device)

                print("✅ Florence-2 loaded successfully (fallback method)")

            except Exception as e2:
                print(f"❌ Fallback loading also failed: {e2}")
                print(
                    "💡 Please try updating transformers: pip install --upgrade transformers"
                )
                return

        try:
            print("Loading SAM2 model...")

            # Get the full path to SAM2 config files
            import sam2

            sam2_base_path = os.path.dirname(sam2.__file__)

            # Try different SAM2 models and configs with full paths
            sam2_models = {
                "base_plus": {
                    "checkpoint": "sam2.1_hiera_base_plus.pt",
                    "config": "sam2.1_hiera_b+.yaml",
                    "name": "SAM2.1 Base Plus",
                },
                "large": {
                    "checkpoint": "sam2.1_hiera_large.pt",
                    "config": "sam2.1_hiera_l.yaml",
                    "name": "SAM2.1 Large",
                },
            }

            # Select the requested model or fallback to available ones
            if self.sam2_model_key in sam2_models:
                selected_models = [sam2_models[self.sam2_model_key]]
                # Add other models as fallback
                fallback_models = [
                    model
                    for key, model in sam2_models.items()
                    if key != self.sam2_model_key
                ]
                selected_models.extend(fallback_models)
            else:
                # Use all models if invalid key provided
                selected_models = list(sam2_models.values())

            sam2_configs = []
            for model_info in selected_models:
                sam2_configs.append(
                    {
                        "checkpoint": os.path.join(
                            os.path.dirname(__file__),
                            "models",
                            model_info["checkpoint"],
                        ),
                        "config": os.path.join(
                            sam2_base_path, "configs", "sam2.1", model_info["config"]
                        ),
                        "name": model_info["name"],
                    }
                )

            sam2_model = None
            for config in sam2_configs:
                try:
                    checkpoint_path = config["checkpoint"]
                    model_cfg = config["config"]

                    if os.path.exists(checkpoint_path) and os.path.exists(model_cfg):
                        print(f"  Trying {config['name']}")
                        print(f"    Checkpoint: {os.path.basename(checkpoint_path)}")
                        print(f"    Config: {os.path.basename(model_cfg)}")

                        # Build SAM2 model with full config path
                        sam2_model = build_sam2(
                            model_cfg, checkpoint_path, device=self.device
                        )
                        self.sam2_predictor = SAM2ImagePredictor(sam2_model)
                        print(f"✅ SAM2 loaded successfully: {config['name']}")
                        break

                except Exception as e:
                    print(f"  ❌ Failed to load {config['name']}: {e}")
                    continue

            if not sam2_model:
                print("❌ All SAM2 loading attempts failed")
                print("Available checkpoints:")
                models_dir = os.path.join(os.path.dirname(__file__), "models")
                for file in os.listdir(models_dir):
                    if file.endswith(".pt"):
                        print(f"  - {file}")
                print("Available configs:")
                config_dir = os.path.join(sam2_base_path, "configs", "sam2.1")
                if os.path.exists(config_dir):
                    for file in os.listdir(config_dir):
                        if file.endswith(".yaml"):
                            print(f"  - {file}")

        except Exception as e:
            print(f"❌ Error loading SAM2: {e}")
            print("Make sure SAM2 checkpoints are available")

    def florence_phrase_grounding(self, image, text_prompt):
        """
        Use Florence-2 to find objects matching the text prompt.

        Args:
            image: PIL Image
            text_prompt: str, e.g., "girl"

        Returns:
            List of bounding boxes and labels
        """
        if not self.florence_model:
            print("❌ Florence-2 model not loaded")
            return []

        try:
            print(f"🔍 Florence grounding for: '{text_prompt}'")

            # Prepare the prompt for phrase grounding
            prompt = f"<CAPTION_TO_PHRASE_GROUNDING>{text_prompt}"
            print(f"  Prompt: {prompt}")
            print(f"  Image size: {image.size}")
            print(f"  Device: {self.device}")

            # Process the image and prompt
            print("  Processing inputs...")
            inputs = self.florence_processor(
                text=prompt, images=image, return_tensors="pt"
            )
            print(f"  Input keys: {list(inputs.keys())}")

            # Move inputs to device if not already
            print("  Moving inputs to device...")
            for key in inputs:
                if hasattr(inputs[key], "to"):
                    print(f"    Moving {key} to {self.device}")
                    inputs[key] = inputs[key].to(self.device)
                    print(
                        f"    {key} shape: {inputs[key].shape if hasattr(inputs[key], 'shape') else 'no shape'}"
                    )
                    print(
                        f"    {key} dtype: {inputs[key].dtype if hasattr(inputs[key], 'dtype') else 'no dtype'}"
                    )
                    print(
                        f"    {key} device: {inputs[key].device if hasattr(inputs[key], 'device') else 'no device'}"
                    )
                    # Check if any values are None
                    if hasattr(inputs[key], "isnan"):
                        nan_count = torch.isnan(inputs[key]).sum().item()
                        print(f"    {key} has {nan_count} NaN values")
                    if inputs[key] is None:
                        print(f"    WARNING: {key} is None!")

            # Generate results
            print("  Generating...")
            print(f"  Model device: {next(self.florence_model.parameters()).device}")
            print(f"  Model dtype: {next(self.florence_model.parameters()).dtype}")

            with torch.no_grad():
                try:
                    # Verify model and inputs before generation
                    print("  Verifying inputs before generation...")
                    for key, value in inputs.items():
                        if value is None:
                            print(f"    ERROR: {key} is None!")
                            return []

                    print("  Calling generate...")
                    generated_ids = self.florence_model.generate(
                        input_ids=inputs["input_ids"],
                        pixel_values=inputs["pixel_values"],
                        max_new_tokens=1024,
                        do_sample=False,
                        num_beams=1,  # Reduce beam search for CPU
                        pad_token_id=(
                            self.florence_processor.tokenizer.pad_token_id
                            if hasattr(self.florence_processor, "tokenizer")
                            else self.florence_processor.pad_token_id
                        ),
                        use_cache=False,  # Disable cache to avoid past_key_values issue
                        return_dict_in_generate=True,
                        output_scores=False,
                    )
                    print(f"  Generated result type: {type(generated_ids)}")

                    # Handle return_dict_in_generate result
                    if hasattr(generated_ids, "sequences"):
                        generated_ids = generated_ids.sequences

                    print(f"  Generated IDs shape: {generated_ids.shape}")
                except Exception as gen_error:
                    print(f"    Primary generation error: {gen_error}")
                    import traceback

                    traceback.print_exc()

                    # Try with even more minimal parameters
                    try:
                        print("  Trying minimal generation...")
                        generated_ids = self.florence_model.generate(
                            input_ids=inputs["input_ids"],
                            pixel_values=inputs["pixel_values"],
                            max_new_tokens=100,
                            do_sample=False,
                            use_cache=False,  # Disable cache to avoid past_key_values issue
                        )
                        print(f"  Minimal generation succeeded: {generated_ids.shape}")
                    except Exception as min_error:
                        print(f"    Minimal generation also failed: {min_error}")
                        import traceback

                        traceback.print_exc()
                        return []

            print("  Decoding results...")
            # Decode results
            generated_text = self.florence_processor.batch_decode(
                generated_ids, skip_special_tokens=False
            )[0]

            print(f"  Generated text: {generated_text}")

            # Parse the results
            parsed_answer = self.florence_processor.post_process_generation(
                generated_text,
                task="<CAPTION_TO_PHRASE_GROUNDING>",
                image_size=(image.width, image.height),
            )

            print(f"  Parsed answer: {parsed_answer}")

            # Extract bounding boxes
            results = []
            if "<CAPTION_TO_PHRASE_GROUNDING>" in parsed_answer:
                grounding_results = parsed_answer["<CAPTION_TO_PHRASE_GROUNDING>"]

                if "bboxes" in grounding_results and "labels" in grounding_results:
                    bboxes = grounding_results["bboxes"]
                    labels = grounding_results["labels"]

                    for bbox, label in zip(bboxes, labels):
                        results.append(
                            {
                                "bbox": bbox,  # [x1, y1, x2, y2]
                                "label": label,
                                "confidence": 1.0,  # Florence doesn't provide confidence
                            }
                        )

            print(f"✅ Found {len(results)} objects: {[r['label'] for r in results]}")
            return results

        except Exception as e:
            print(f"❌ Florence grounding error: {e}")
            return []

    def sam2_segmentation(self, image, bboxes):
        """
        Use SAM2 to generate segmentation masks from bounding boxes.

        Args:
            image: PIL Image
            bboxes: List of bounding boxes [[x1, y1, x2, y2], ...]

        Returns:
            List of segmentation masks
        """
        if not self.sam2_predictor:
            print("❌ SAM2 model not loaded")
            return []

        try:
            print(f"🎯 SAM2 segmentation for {len(bboxes)} bounding boxes")

            # Convert PIL to numpy array
            image_array = np.array(image)

            # Set image for SAM2 predictor
            self.sam2_predictor.set_image(image_array)

            all_masks = []

            for i, bbox in enumerate(bboxes):
                # Convert bbox to input box format for SAM2
                input_box = np.array([bbox])  # SAM2 expects [[x1, y1, x2, y2]]

                # Generate mask
                masks, scores, logits = self.sam2_predictor.predict(
                    point_coords=None,
                    point_labels=None,
                    box=input_box[0],
                    multimask_output=False,
                )

                # Take the best mask (first one when multimask_output=False)
                mask = masks[0]
                score = scores[0]

                all_masks.append({"mask": mask, "score": score, "bbox": bbox})

                print(f"  Generated mask {i+1} (score: {score:.3f})")

            print(f"✅ Generated {len(all_masks)} segmentation masks")
            return all_masks

        except Exception as e:
            print(f"❌ SAM2 segmentation error: {e}")
            return []

    def create_red_mask_overlay(self, image, masks, output_path):
        """
        Create red mask overlay on the original image.

        Args:
            image: PIL Image
            masks: List of mask dictionaries from SAM2
            output_path: str, output file path
        """
        try:
            print(f"🎨 Creating red mask overlay with {len(masks)} masks")

            # Convert PIL to numpy
            image_array = np.array(image)
            overlay = image_array.copy()

            # Create red overlay for each mask
            red_color = [255, 0, 0]  # Red color
            alpha = 0.5  # Transparency

            for i, mask_data in enumerate(masks):
                mask = mask_data["mask"]

                # Ensure mask is boolean for indexing
                if mask.dtype != bool:
                    mask = mask.astype(bool)

                # Apply red overlay where mask is True
                overlay[mask] = (
                    overlay[mask] * (1 - alpha) + np.array(red_color) * alpha
                )

            # Convert back to PIL and save
            result_image = Image.fromarray(overlay.astype(np.uint8))
            result_image.save(output_path)

            print(f"✅ Saved red mask overlay: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating red mask overlay: {e}")
            return None

    def create_transparent_cutout(self, image, masks, output_path):
        """
        Create image where everything except segmented targets is transparent.

        Args:
            image: PIL Image
            masks: List of mask dictionaries from SAM2
            output_path: str, output file path
        """
        try:
            print(f"✂️ Creating transparent cutout with {len(masks)} masks")

            # Convert PIL to RGBA (with alpha channel)
            if image.mode != "RGBA":
                image_rgba = image.convert("RGBA")
            else:
                image_rgba = image.copy()

            # Convert to numpy array
            image_array = np.array(image_rgba)

            # Create combined mask (union of all masks)
            height, width = image_array.shape[:2]
            combined_mask = np.zeros((height, width), dtype=bool)

            for i, mask_data in enumerate(masks):
                mask = mask_data["mask"]

                # Ensure mask is boolean
                if mask.dtype != bool:
                    mask = mask.astype(bool)

                # Add to combined mask
                combined_mask = combined_mask | mask
                print(f"  Added mask {i+1} to cutout")

            # Set alpha channel: 255 (opaque) for segmented areas, 0 (transparent) for background
            image_array[:, :, 3] = np.where(combined_mask, 255, 0)

            # Convert back to PIL and save as PNG (to preserve transparency)
            result_image = Image.fromarray(image_array, "RGBA")

            # Ensure output is PNG for transparency support
            if not output_path.lower().endswith(".png"):
                output_path = os.path.splitext(output_path)[0] + ".png"

            result_image.save(output_path, "PNG")

            print(f"✅ Saved transparent cutout: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating transparent cutout: {e}")
            return None

    def process_image(
        self, image_path, text_prompt, output_path=None, output_type="overlay"
    ):
        """
        Complete pipeline: Florence grounding + SAM2 segmentation + output generation.

        Args:
            image_path: str, path to input image
            text_prompt: str, search query (e.g., "girl")
            output_path: str, optional output path
            output_type: str, 'overlay' for red mask or 'cutout' for transparent background
        """
        try:
            print(f"\n🚀 Processing: {image_path}")
            print(f"🔍 Searching for: '{text_prompt}'")
            print(f"📄 Output type: {output_type}")

            # Load image
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                return

            image = Image.open(image_path).convert("RGB")
            print(f"📷 Loaded image: {image.size}")

            # Step 1: Florence phrase grounding
            grounding_results = self.florence_phrase_grounding(image, text_prompt)

            if not grounding_results:
                print(f"❌ No objects found for '{text_prompt}'")
                return

            # Extract bounding boxes
            bboxes = [result["bbox"] for result in grounding_results]

            # Step 2: SAM2 segmentation
            segmentation_masks = self.sam2_segmentation(image, bboxes)

            if not segmentation_masks:
                print("❌ No segmentation masks generated")
                return

            # Step 3: Create output based on type
            if not output_path:
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_dir = os.path.dirname(image_path)
                if output_type == "cutout":
                    output_path = os.path.join(output_dir, f"{base_name}_cutout.png")
                else:
                    output_path = os.path.join(output_dir, f"{base_name}_mask.jpg")

            if output_type == "cutout":
                result_path = self.create_transparent_cutout(
                    image, segmentation_masks, output_path
                )
            else:
                result_path = self.create_red_mask_overlay(
                    image, segmentation_masks, output_path
                )

            if result_path:
                print(f"\n✅ Pipeline completed successfully!")
                print(f"📁 Output saved: {result_path}")

                # Print summary
                print(f"\n📊 Summary:")
                print(f"  - Found {len(grounding_results)} objects")
                print(f"  - Generated {len(segmentation_masks)} masks")
                print(f"  - Objects: {[r['label'] for r in grounding_results]}")
                print(f"  - Output type: {output_type}")

        except Exception as e:
            print(f"❌ Pipeline error: {e}")


def main():
    """Florence-2 + SAM2 segmentation pipeline with command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Florence-2 + SAM2 Segmentation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lazy_segment.py input.jpg "girl" output.png
  python lazy_segment.py /path/to/image.jpg "person with hat" /path/to/result.jpg
  python lazy_segment.py image.png "car" (auto-generate output path)
  python lazy_segment.py image.jpg "girl" --cutout (create transparent cutout)
  python lazy_segment.py image.jpg "car" result.png --cutout (transparent cutout with custom path)
        """,
    )

    parser.add_argument("image_path", help="Path to the input image file")

    parser.add_argument(
        "text_prompt",
        help="Text prompt to search for in the image (e.g., 'girl', 'car', 'person with hat')",
    )

    parser.add_argument(
        "output_path",
        nargs="?",  # Optional argument
        help="Path for the output image (optional - will auto-generate if not provided)",
    )

    parser.add_argument(
        "--cutout",
        action="store_true",
        help="Create transparent cutout instead of red mask overlay",
    )

    parser.add_argument(
        "--models-dir",
        default=None,
        help="Custom directory for storing models (optional)",
    )

    parser.add_argument(
        "--model",
        choices=["base_plus", "large"],
        default="base_plus",
        help="Choose SAM2 model variant (base_plus or large)",
    )

    args = parser.parse_args()

    print("[SEGMENT] Florence-2 + SAM2 Segmentation Pipeline")
    print("=" * 50)

    # Validate input image
    if not os.path.exists(args.image_path):
        print(f"[ERROR] Input image not found: {args.image_path}")
        sys.exit(1)

    # Determine output type
    output_type = "cutout" if args.cutout else "overlay"

    # Show configuration
    print(f"[INPUT] Input image: {args.image_path}")
    print(f"[PROMPT] Text prompt: '{args.text_prompt}'")
    print(
        f"[TYPE] Output type: {'Transparent cutout' if args.cutout else 'Red mask overlay'}"
    )
    print(f"[MODEL] SAM2 model: {args.model}")
    if args.output_path:
        print(f"[OUTPUT] Output path: {args.output_path}")
    else:
        suffix = "_cutout.png" if args.cutout else "_mask.jpg"
        print(f"💾 Output path: Auto-generated ({suffix})")

    # Show model storage location
    if args.models_dir:
        models_dir = args.models_dir
    else:
        models_dir = os.path.join(os.path.dirname(__file__), "models")
    print(f"[MODELS] Models directory: {os.path.abspath(models_dir)}")
    print()

    # Initialize pipeline
    try:
        pipeline = FloSAM2Pipeline(sam2_model_key=args.model)

        # Run the complete pipeline
        pipeline.process_image(
            args.image_path, args.text_prompt, args.output_path, output_type
        )

    except KeyboardInterrupt:
        print("\n[STOP] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Pipeline initialization error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
