"""
Batch Processor for Declare-SBMN Mining
Processes multiple .xes files from a folder structure and tracks processing time.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from pprint import pprint
from Declare4Py.ProcessMiningTasks.Discovery.DeclareMiner import DeclareMiner
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from declaresbmn_layered import sbmn_mining
from sbmn_model_functions import parse_sbmn_model, generate_json_from_sbmn
from assertiontests_functions import SBMNValidator


class BatchProcessor:
    """Process multiple .xes files and track processing time."""
    
    def __init__(self, main_folder, output_folder="OUTPUTS", 
                 min_support_layer1=0.6, min_support_layer2=0.1,
                 itemsets_support_layer1=0.01, itemsets_support_layer2=0.00001):
        """
        Initialize batch processor.
        
        Args:
            main_folder: Main folder containing subfolders with .xes files
            output_folder: Folder to save outputs
            min_support_layer1: Minimum support for first layer mining
            min_support_layer2: Minimum support for second layer mining
            itemsets_support_layer1: Itemsets support for first layer
            itemsets_support_layer2: Itemsets support for second layer
        """
        self.main_folder = Path(main_folder)
        self.output_folder = Path(output_folder)
        self.min_support_layer1 = min_support_layer1
        self.min_support_layer2 = min_support_layer2
        self.itemsets_support_layer1 = itemsets_support_layer1
        self.itemsets_support_layer2 = itemsets_support_layer2
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(exist_ok=True)
        
        # Initialize results tracking
        self.processing_results = []
        
    def find_xes_files(self):
        """
        Find all .xes files in the main folder and subfolders.
        
        Returns:
            List of tuples (file_path, relative_path)
        """
        xes_files = []
        for root, dirs, files in os.walk(self.main_folder):
            for file in files:
                if file.endswith('.xes'):
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(self.main_folder)
                    xes_files.append((full_path, relative_path))
        
        return xes_files
    
    def process_single_file(self, file_path, relative_path):
        """
        Process a single .xes file and track processing time.
        
        Args:
            file_path: Path to the .xes file
            relative_path: Relative path from main folder
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n{'='*80}")
        print(f"Processing: {relative_path}")
        print(f"{'='*80}")
        
        result = {
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'times': {}
        }
        
        try:
            # Start total time
            total_start = time.time()
            
            # Load event log
            print("\n[1/5] Loading event log...")
            load_start = time.time()
            event_log = D4PyEventLog(case_name="case:concept:name")
            event_log.parse_xes_log(str(file_path))
            load_time = time.time() - load_start
            result['times']['load_log'] = load_time
            print(f"   ✓ Loaded in {load_time:.2f}s")
            
            # First layer mining
            print("\n[2/5] Mining constraints - First Layer...")
            layer1_start = time.time()
            discovery_1 = DeclareMiner(
                log=event_log,
                consider_vacuity=False,
                min_support=self.min_support_layer1,
                itemsets_support=self.itemsets_support_layer1,
                max_declare_cardinality=3
            )
            discovered_model_first_layer: DeclareModel = discovery_1.run()
            layer1_time = time.time() - layer1_start
            result['times']['layer1_mining'] = layer1_time
            result['layer1_constraints_count'] = len(discovered_model_first_layer.serialized_constraints)
            print(f"   ✓ First layer mining completed in {layer1_time:.2f}s")
            print(f"   ✓ Extracted {len(discovered_model_first_layer.serialized_constraints)} constraints")
            
            # SBMN mining (includes second layer)
            print("\n[3/5] SBMN Mining (Second Layer)...")
            sbmn_start = time.time()
            matrix, sbmn = sbmn_mining(discovered_model_first_layer.serialized_constraints, event_log)
            sbmn_time = time.time() - sbmn_start
            result['times']['sbmn_mining'] = sbmn_time
            result['sbmn_model_size'] = len(sbmn)
            print(f"   ✓ SBMN mining completed in {sbmn_time:.2f}s")
            print(f"   ✓ Generated {len(sbmn)} SBMN elements")
            
            # Validate model
            print("\n[4/5] Validating SBMN model...")
            validation_start = time.time()
            sbmn_model = parse_sbmn_model(sbmn)
            validator = SBMNValidator()
            validation_result = validator.validate_model(sbmn_model)
            validation_time = time.time() - validation_start
            result['times']['validation'] = validation_time
            result['validation_result'] = validation_result
            print(f"   ✓ Validation completed in {validation_time:.2f}s")
            
            # Generate JSON output
            print("\n[5/5] Generating JSON output...")
            json_start = time.time()
            
            # Create subfolder structure in output
            output_subfolder = self.output_folder / relative_path.parent
            output_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Generate file name
            log_name = file_path.stem  # filename without extension
            output_json_path = output_subfolder / f"sbmn_{log_name}.json"
            
            # Generate JSON
            json_model = generate_json_from_sbmn(matrix, {}, str(output_json_path))
            json_time = time.time() - json_start
            result['times']['json_generation'] = json_time
            result['output_json'] = str(output_json_path)
            print(f"   ✓ JSON generated in {json_time:.2f}s")
            print(f"   ✓ Saved to: {output_json_path}")
            
            # Calculate total time
            total_time = time.time() - total_start
            result['times']['total'] = total_time
            result['success'] = True
            
            print(f"\n✓ COMPLETED in {total_time:.2f}s")
            
        except Exception as e:
            result['error'] = str(e)
            result['times']['total'] = time.time() - total_start
            print(f"\n✗ ERROR: {e}")
        
        return result
    
    def process_all_files(self):
        """
        Process all .xes files found in the main folder structure.
        
        Returns:
            Summary statistics
        """
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING STARTED")
        print(f"{'='*80}")
        print(f"Main folder: {self.main_folder}")
        print(f"Output folder: {self.output_folder}")
        
        # Find all .xes files
        xes_files = self.find_xes_files()
        print(f"\nFound {len(xes_files)} .xes file(s)")
        
        if not xes_files:
            print("\n⚠ No .xes files found!")
            return None
        
        # Process each file
        batch_start = time.time()
        
        for i, (file_path, relative_path) in enumerate(xes_files, 1):
            print(f"\n\n[File {i}/{len(xes_files)}]")
            result = self.process_single_file(file_path, relative_path)
            self.processing_results.append(result)
        
        batch_total_time = time.time() - batch_start
        
        # Generate summary
        summary = self.generate_summary(batch_total_time)
        
        # Save results to JSON
        self.save_results(summary)
        
        return summary
    
    def generate_summary(self, batch_total_time):
        """Generate processing summary statistics."""
        successful = [r for r in self.processing_results if r['success']]
        failed = [r for r in self.processing_results if not r['success']]
        
        summary = {
            'batch_info': {
                'main_folder': str(self.main_folder),
                'output_folder': str(self.output_folder),
                'timestamp': datetime.now().isoformat(),
                'total_files': len(self.processing_results),
                'successful': len(successful),
                'failed': len(failed),
                'batch_total_time': batch_total_time
            },
            'mining_parameters': {
                'min_support_layer1': self.min_support_layer1,
                'min_support_layer2': self.min_support_layer2,
                'itemsets_support_layer1': self.itemsets_support_layer1,
                'itemsets_support_layer2': self.itemsets_support_layer2
            },
            'time_statistics': {},
            'detailed_results': self.processing_results
        }
        
        # Calculate time statistics for successful runs
        if successful:
            time_keys = ['load_log', 'layer1_mining', 'sbmn_mining', 'validation', 'json_generation', 'total']
            for key in time_keys:
                times = [r['times'].get(key, 0) for r in successful if key in r['times']]
                if times:
                    summary['time_statistics'][key] = {
                        'min': min(times),
                        'max': max(times),
                        'avg': sum(times) / len(times),
                        'total': sum(times)
                    }
        
        return summary
    
    def save_results(self, summary):
        """Save processing results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_folder / f"batch_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Total files: {summary['batch_info']['total_files']}")
        print(f"Successful: {summary['batch_info']['successful']}")
        print(f"Failed: {summary['batch_info']['failed']}")
        print(f"Total batch time: {summary['batch_info']['batch_total_time']:.2f}s")
        
        if summary['time_statistics']:
            print(f"\nTime Statistics (successful runs):")
            for key, stats in summary['time_statistics'].items():
                print(f"  {key}:")
                print(f"    Min: {stats['min']:.2f}s | Max: {stats['max']:.2f}s | Avg: {stats['avg']:.2f}s")
        
        if summary['batch_info']['failed'] > 0:
            print(f"\nFailed files:")
            for result in self.processing_results:
                if not result['success']:
                    print(f"  - {result['relative_path']}: {result['error']}")
        
        print(f"\nResults saved to: {results_file}")
        
        return results_file


def main():
    """Main entry point for batch processing."""
    
    # Configuration
    MAIN_FOLDER = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS4"  # Change to your main folder
    OUTPUT_FOLDER = "OUTPUTS"
    
    # Mining parameters
    MIN_SUPPORT_LAYER1 = 0.6
    MIN_SUPPORT_LAYER2 = 0.1
    ITEMSETS_SUPPORT_LAYER1 = 0.01
    ITEMSETS_SUPPORT_LAYER2 = 0.00001
    
    # Create processor
    processor = BatchProcessor(
        main_folder=MAIN_FOLDER,
        output_folder=OUTPUT_FOLDER,
        min_support_layer1=MIN_SUPPORT_LAYER1,
        min_support_layer2=MIN_SUPPORT_LAYER2,
        itemsets_support_layer1=ITEMSETS_SUPPORT_LAYER1,
        itemsets_support_layer2=ITEMSETS_SUPPORT_LAYER2
    )
    
    # Process all files
    summary = processor.process_all_files()
    
    print("\n✓ Batch processing completed!")


if __name__ == "__main__":
    main()
