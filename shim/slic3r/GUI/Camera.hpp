#pragma once
namespace Slic3r { namespace GUI {
struct Camera {
    enum class EType : unsigned char { Unknown, Ortho, Perspective, Num_types };
    enum class ViewAngleType : unsigned char {
        Iso = 0, Top_Front, Left, Right, Top, Bottom, Front, Rear, Count_ViewAngleType,
        Top_Plate, Iso_1, Iso_2, Iso_3
    };
};
}}
