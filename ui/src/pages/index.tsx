import Navbar from '../components/Navbar'
import HeroSection from '../components/HeroSection'
import { useState, useCallback } from 'react'


export default function Home(){
   const [start, setStart] = useState<boolean>(false)
   const resetStart = useCallback((prop: boolean) => setStart(prop), []);

  return(
    <div className='bg-gradient-to-r from-[#E0F5F8] to-transparent '>

    <Navbar resetStart={resetStart}/>
    <HeroSection  start={start} setStart={setStart}/>
    </div>
  )
}