# Evolved BBO Instances

This repository makes available the instances used in the paper: M.A. Muñoz and K. Smith-Miles ["Generating New Space-Filling Test Instances for Continuous Black-Box Optimization"](doi:10.1162/evco_a_00262) Evol. Comput. 2019. It provides instances from four sources.

- Generated using the methodology described in the paper above in the function ```munozsmithmiles.m```.
- Those from the "Comparing Continuous Optimization benchmarking platform" v13.09, released in 2011. These are provided as reference, as newer versions can be downloaded [here](https://github.com/numbbo/coco).
- Most of the instances described in: W.B. Langdon and R. Poli ["Evolving problems to learn about Particle Swarm Optimizers and other search algorithms"](doi:10.1109/TEVC.2006.886448) IEEE Trans. Evol. Comput. 11(5)561-578, 2007. through the function ```langdonpoli.m```
- Clustering based instances following the methodology by: M. Gallagher ["Towards improved benchmarking of black-box optimization
algorithms using clustering problems"](doi:10.1007/s00500-016-2094-1) Soft Comput. 20(10)3835–3849, 2016. through the function ```clustergallagher.m```

Details on how to use each function are given in the respective file.

## Installation Instructions

The only requirement for the software to run is to have a current version of [MATLAB](http://www.mathworks.com). It has been tested and known to work properly in version r2018b, but it should work in early versions. Most of the code is vectorized, so it should be fast (for MATLAB).

## Contact

If you have any suggestions or ideas (e.g. for new features), or if you encounter any problems while running the code, please use the [issue tracker](https://github.com/andremun/EVOBBO_Instances/issues) or contact us through the MATILDA's [Queries and Feedback](http://matilda.unimelb.edu.au/contact-us) page.

## Acknowledgements

Funding for the development of this code was provided by the Australian Research Council through the Australian Laureate Fellowship FL140100012.
