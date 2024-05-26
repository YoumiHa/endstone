// Copyright (c) 2024, The Endstone Project. (https://endstone.dev) All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include "bedrock/bedrock.h"
#include "bedrock/world/level/storage/level_seed.h"

class LevelSettings {
public:
    [[nodiscard]] LevelSeed64 getSeed() const
    {
        return seed_;
    }

    void setRandomSeed(LevelSeed64 seed)
    {
        seed_ = seed;
    }

private:
    LevelSeed64 seed_;
#ifdef _WIN32
    size_t pad_[1248 / 8 - 1];
#else
    size_t pad_[1024 / 8 - 1];
#endif
};
BEDROCK_STATIC_ASSERT_SIZE(LevelSettings, 1248, 1024);
