import requests
import os
import json
from config import client, DEPLOYMENT_NAME, DALLE_DEPLOYMENT_NAME


class DeliverableGenerator:
    """Simplified orchestrator for the AI Deliverable Generator."""
    def __init__(self, client_instance=None, deployment_name=None, dalle_deployment_name=None,temperature: float = 0.7, max_tokens: int = 4096, top_p: float = 0.95, system_message: str = None):
        self.client = client_instance or client
        self.deployment_name = deployment_name or DEPLOYMENT_NAME
        self.dalle_deployment_name = dalle_deployment_name or DALLE_DEPLOYMENT_NAME
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.system_message = system_message

    def _load_prompt(self, prompt_path, **kwargs):
        """Load prompt from file and replace placeholders"""
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            
            # Replace all placeholders
            for key, value in kwargs.items():
                placeholder = "{" + key + "}"
                # Handle both string and dict values
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                elif not isinstance(value, str):
                    value = str(value)
                prompt = prompt.replace(placeholder, value)
            
            return prompt
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        except Exception as e:
            raise Exception(f"Error loading prompt from {prompt_path}: {str(e)}")

    def generate_deliverable(self, prompt: str, system_message: str = None) -> str:
        """Generate deliverable from a single prompt string."""
        sys_msg = system_message or self.system_message
        if not sys_msg:
            sys_msg = "You are an expert proposal generator for consulting and advisory services."
        try:
            print("Using deployment name:", self.deployment_name)
            print('Prompt for generation:', prompt)
            print('System message:', sys_msg)
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating content: {e}")

    def generate_problem_requirements(self, business_problem, tech_stack, time_constraint, resource_constraints):
        """Step 1: Generate problem requirements"""
        try:
            prompt = self._load_prompt(
                "prompts/step1_problem_requirements_prompt.txt",
                business_problem=business_problem,
                tech_stack=tech_stack,
                time_constraint=time_constraint,
                resource_constraints=resource_constraints
            )
            
            print("\n" + "="*60)
            print("=== Step 1: Generating Problem Requirements ===")
            print("="*60)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_message or "You are a business analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            
            response_text = response.choices[0].message.content
            
            # Clean response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```"):
                # Remove markdown code blocks
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(lines).strip()
            
            result = json.loads(response_text)
            print("✓ Problem requirements generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in Step 1: {e}")
            print(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Error in Step 1: {e}")
            raise

    def generate_technical_plan(self, problem_requirements):
        """Step 2: Generate technical plan from problem requirements"""
        try:
            prompt = self._load_prompt(
                "prompts/step2_technical_plan_prompt.txt",
                problem_requirements=problem_requirements
            )
            
            print("\n" + "="*60)
            print("=== Step 2: Generating Technical Plan ===")
            print("="*60)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_message or "You are a solutions architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            
            response_text = response.choices[0].message.content
            
            # Clean response
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(lines).strip()
            
            result = json.loads(response_text)
            print("✓ Technical plan generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in Step 2: {e}")
            print(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Error in Step 2: {e}")
            raise

    def generate_deliverable_plan(self, technical_plan):
        """Step 3: Generate deliverable plan from technical plan"""
        try:
            prompt = self._load_prompt(
                "prompts/step3_deliverable_plan_prompt.txt",
                technical_plan=technical_plan
            )
            
            print("\n" + "="*60)
            print("=== Step 3: Generating Deliverable Plan ===")
            print("="*60)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_message or "You are a project manager."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            
            response_text = response.choices[0].message.content
            
            # Clean response
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(lines).strip()
            
            result = json.loads(response_text)
            print("✓ Deliverable plan generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in Step 3: {e}")
            print(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Error in Step 3: {e}")
            raise

    def generate_data_plan(self, technical_plan):
        """Step 3 (Alternative): Generate data plan from technical plan"""
        try:
            prompt = self._load_prompt(
                "prompts/step4_data_plan_prompt.txt",
                technical_plan=technical_plan
            )
            
            print("\n" + "="*60)
            print("=== Step 4: Generating Data Plan ===")
            print("="*60)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_message or "You are a data architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            
            response_text = response.choices[0].message.content
            
            # Clean response
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(lines).strip()
            
            result = json.loads(response_text)
            print("✓ Data plan generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in Step 3 (Data Plan): {e}")
            print(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Error in Step 3 (Data Plan): {e}")
            raise

    def generate_full_deliverable_pipeline(self, deliverable_type, business_problem, tech_stack, time_constraint, resource_constraints):
        """Execute full pipeline based on deliverable type"""
        
        print("\n" + "="*80)
        print("🚀 STARTING MULTI-STEP PIPELINE GENERATION")
        print(f"📋 Deliverable Type: {deliverable_type}")
        print("="*80)
        
        try:
            # Step 1: Problem Requirements
            problem_reqs = self.generate_problem_requirements(
                business_problem, tech_stack, time_constraint, resource_constraints
            )
            
            # Step 2: Technical Plan
            technical_plan = self.generate_technical_plan(problem_reqs)
            
            # Step 3: Type-specific deliverable
            deliverable_plan = self.generate_deliverable_plan(technical_plan)
            
            # Step 4: Data Plan (if applicable)
            data_plan = self.generate_data_plan(technical_plan)

            final_output = {
                    "problem-requirements": problem_reqs,
                    "technical-plan": technical_plan,
                    "deliverable-plan": deliverable_plan,
                    "data-plan": data_plan
                }
            
            # if deliverable_type in ["summary", "roadmap", "architecture"]:
            #     deliverable_plan = self.generate_deliverable_plan(technical_plan)
                
            #     final_output = {
            #         "problem-requirements": problem_reqs,
            #         "technical-plan": technical_plan,
            #         "deliverable-plan": deliverable_plan
            #     }
            
            # elif deliverable_type == "data-schema":
            #     data_plan = self.generate_data_plan(technical_plan)
                
            #     final_output = {
            #         "problem-requirements": problem_reqs,
            #         "technical-plan": technical_plan,
            #         "data-plan": data_plan
            #     }
            
            # else:
            #     raise ValueError(f"Unknown deliverable type: {deliverable_type}")
            
            print("\n" + "="*80)
            print("✅ PIPELINE GENERATION COMPLETE")
            print("="*80)
            
            return final_output
            
        except Exception as e:
            print("\n" + "="*80)
            print(f"❌ PIPELINE GENERATION FAILED: {e}")
            print("="*80)
            raise

    def generate_image(self, prompt):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        deployment = os.getenv("AZURE_DALL_E_DEPLOYMENT")

        url = f"{endpoint}openai/deployments/{deployment}/images/generations?api-version=2024-02-01" 

        print("\n" + "="*60)
        print("=== Step 5: Generating Architecture Diagram ===")
        print("="*60)

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "n": 1
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("✓ Architecture diagram generated successfully")
            return response.json().get("data", [{}])[0].get("url", "")
        except Exception as e:
            print(f"Image generation failed: {e}")
            return ""

    def generate_slides(self, content, slide_count=12):
        """Generate presentation slides from pipeline content"""
        try:
            import json
            
            content_str = json.dumps(content, indent=2)
            
            prompt = self._load_prompt(
                "prompts/step6_slide_generation_prompt.txt",
                content=content_str,
                slide_count=slide_count
            )
            
            print("\n" + "="*60)
            print("=== Generating Presentation Slides ===")
            print("="*60)
            
            response = self.generate_deliverable(
                prompt=prompt,
                system_message="You are a presentation expert. Return only valid JSON array of slides."
            )
            
            # Clean response
            response_text = response.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(lines).strip()
            
            # Parse JSON
            slides = json.loads(response_text)
            
            print(f"✓ Generated {len(slides)} slides successfully")
            
            return slides
            
        except json.JSONDecodeError as e:
            print(f"❌ Slide generation JSON parsing failed: {e}")
            print(f"Response preview: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"❌ Slide generation failed: {e}")
            raise
