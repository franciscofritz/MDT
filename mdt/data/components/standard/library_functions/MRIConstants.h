/**
 * Author = Robbert Harms
 * Date = 2014-09-21
 * License = LGPL v3
 * Maintainer = Robbert Harms
 * Email = robbert.harms@maastrichtuniversity.nl
 */

/**
 * This file provides a list of MRI specific constants used throughout the compartment CL functions.
 */

/**
 * Gamma represent the gyromagnetic ratio of protons in water (nucleus of H)
 * and are in units of (rad s^-1 T^-1)
 **/
#ifndef GAMMA_H
    #define GAMMA_H 267.5987E6
#endif

/**
 * The same GAMMA as defined above but then divided by 2*pi, in units of s^-1 T^-1
 **/
#ifndef GAMMA_H_HZ
    #define GAMMA_H_HZ (GAMMA_H / (2 * M_PI))
#endif

/**
 * The square of the original GAMMA defined above
 */
#ifndef GAMMA_H_SQ
    #define GAMMA_H_SQ (GAMMA_H * GAMMA_H)
#endif

/**
 * The square of the GAMMA divided by 2*pi from above
 */
#ifndef GAMMA_H_HZ_SQ
    #define GAMMA_H_HZ_SQ (GAMMA_H_HZ * GAMMA_H_HZ)
#endif
